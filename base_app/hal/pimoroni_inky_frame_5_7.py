# ----------------------------------------------------------------------------
# pimoroni_inky_frame_5_7.py: HAL for Pimoroni InkyFrame 5.7
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/circuitpython-base-app
# ----------------------------------------------------------------------------

import board
import time
import keypad
from digitalio import DigitalInOut, Direction

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

  def shutdown(self):
    """ turn off power by pulling enable pin low """
    self._wait_for_display()
    board.ENABLE_DIO.value = 0

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

impl = HALInkyFrame57()
