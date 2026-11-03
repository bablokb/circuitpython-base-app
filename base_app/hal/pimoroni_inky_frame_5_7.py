# ----------------------------------------------------------------------------
# pimoroni_inky_frame_5_7.py: HAL for Pimoroni InkyFrame 5.7
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/circuitpython-base-app
# ----------------------------------------------------------------------------

import alarm
import board
import time
import keypad
import supervisor

from .hal_base import HalBase

class HALInkyFrame57(HalBase):
  """ InkyFrame 5.7 specific HAL-class """

  def __init__(self):
    """ constructor """
    super().__init__()
    self.LED = board.LED_ACT
    self.eink = True
    self.gamut = "acep_7colour"
    self.RTC = "PCF85063"
    # BUTTONS is empty, since they are behind a shift-register
    if not getattr(self,"button_names",None):
      self.button_names = ["A", "B", "C", "D", "E"]
    if not getattr(self,"w_button_names",None):
      self.w_button_names = ["A", "B", "C", "D", "E"]

  # --- deep-sleep   ---------------------------------------------------------

  def deep_sleep(self, alarms=[], wakeup=None):
    """ activate deep-sleep.
    When running on batteries, this is never called because shutdown() turns
    power off. Otherwise, deep-sleep is a fake deep-sleep.
    For this special board, the buttons don't trigger a wakeup, since they are
    behind a shift-register. So don't enter (fake) deep-sleep but loop instead
    and wait until wakeup expires or a button is pressed.
    """

    if not wakeup:
      wakeup = sys.maxsize
    self.msg(f"{board.board_id}: deep-sleep: loop until wakeup or button")
    alarm.sleep_memory[0] = 42
    alarm.sleep_memory[1] = 99
    while time.time() < wakeup:
      ev = self.get_key_event()
      if ev:
        self.msg(f"{board.board_id}: deep-sleep: button {ev[0]} pressed")
        alarm.sleep_memory[1] = ev[0]
        break
      time.sleep(0.1)
    self.reset()

  # --- turn power off   -----------------------------------------------------

  def shutdown(self, wakeup):
    """ turn off power by pulling enable pin low. This is a noop when running
    on usb-power.
    """
    #self._wait_for_display()
    if wakeup and self._rtc_ext:
      self._rtc_ext.set_alarm(wakeup)
    board.POWER_OFF()

  # --- helper method: don't turn power off while busy   ---------------------

  def _wait_for_display(self):
    """ wait for display update to finish """

    keypad = self.keypad()

    # we check the busy-pin of the shift-register
    queue = keypad.events
    while True:
      if not len(queue):
        time.sleep(0.1)
        continue
      ev = queue.get()
      if ev.key_number == board.KEYCODES.INKY_BUS and ev.pressed:
        # i.e. busy-pin is high, so no longer busy
        return

  # --- use a keypad based on class ShiftRegisterKeys   ----------------------

  def get_keypad(self, hal):
    """ return configured keypad """

    return keypad.ShiftRegisterKeys(
      clock = board.SWITCH_CLK,
      data  = board.SWITCH_OUT,
      latch = board.SWITCH_LATCH,
      key_count = 8,
      value_to_latch = True,
      value_when_pressed = True
      )

  # --- return next pending key event   ----------------------------------------

  def get_key_event(self, ignore_released=True):
    """ return next key event. Override base class behavior."""

    ev = super().get_key_event(ignore_released=ignore_released)
    if ev and ev[0] > 2:
      return (7-ev[0], ev[1])
    return None

  # --- query wake-pin   -----------------------------------------------------

  def get_wake_button(self):
    """ return wake button index or None (e.g. for time-alarm) """

    self.msg(f"{board.board_id}: _get_wake_button() mit {int(alarm.sleep_memory[0])}")
    if int(alarm.sleep_memory[0]) == 42:
      # waking up from fake deep-sleep
      index = int(alarm.sleep_memory[1])
      if index < 5:
        self.msg(f"{board.board_id}: wake-button from fake deep-sleep: {index}")
        return index
      else:
        return None

    # else query real wake up button
    for index, pin in enumerate([board.KEYCODES.SW_A, board.KEYCODES.SW_B,
                                 board.KEYCODES.SW_C, board.KEYCODES.SW_D,
                                 board.KEYCODES.SW_E,]):
      if board.ON_RESET_PRESSED(pin):
        return index
    return None

impl = HALInkyFrame57()
