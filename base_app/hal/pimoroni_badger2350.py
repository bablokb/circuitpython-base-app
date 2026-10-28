# ----------------------------------------------------------------------------
# pimoroni_badger2350.py: HAL for Pimoroni Badger2350
#
# Note: deep-sleep needs a patched version of CircuitPython, see
# https://github.com/bablokb/circuitpython-patches
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/circuitpython-base-app
# ----------------------------------------------------------------------------

import time
import board
from digitalio import DigitalInOut, Pull, Direction
import supervisor

from .hal_base import HalBase

class HalBadger2350(HalBase):
  """ Badger2350 specific HAL-class """

  def __init__(self):
    """ constructor """
    super().__init__()
    self.eink = True
    self.gamut = "gray_4"
    self.RTC = "PCF85063"
    # BUTTONS is empty in super-class, but might be tweaked in hw_config
    if not getattr(self,"BUTTONS",None):
      # format is ([pin, ...], value, pull)
      self.BUTTONS = ([board.SW_A, board.SW_B, board.SW_C,
                       board.SW_DOWN, board.SW_UP, board.SW_HOME],
                      False, True)
    if not getattr(self,"WAKE_PINS",None):
      # format is ([pin, ...], value, edge, pull)
      self.WAKE_PINS = ([board.SW_A, board.SW_B, board.SW_C,
                         board.SW_DOWN, board.SW_UP],
                        False, True, True)

    # test for usb-connection
    self._connected = supervisor.runtime.usb_connected

  # --- battery level   ------------------------------------------------------

  def bat_level(self):
    """ return battery level """
    from analogio import AnalogIn

    sum_vbat = 0
    sum_vref = 0
    adc_vbat = AnalogIn(board.VBAT_SENSE)
    adc_vref = AnalogIn(board.SENSE_1V1)

    for _ in range(10):
      sum_vbat += adc_vbat.value
      sum_vref += adc_vref.value
    adc_vbat.deinit()
    adc_vref.deinit()
    return 2.2*sum_vbat/sum_vref

  # --- pin alarms   ---------------------------------------------------------

  def get_pin_alarms(self, hal):
    """ return pin-alarms: buttons are behind an interrupt pin unless connected
    """
    if self._connected:
      return super().get_pin_alarms(hal)
    import alarm
    return [alarm.pin.PinAlarm(board.SW_INT, value=False, edge=True,
                               pull=True)
            ]

  # --- deep-sleep   ---------------------------------------------------------

  def deep_sleep(self, alarms=[], wakeup=None):
    """ activate deep-sleep.
    The default merges all alarms passed as arguments with
    pin-alarms defined via get_pin_alarms().
    """
    try:
      import alarm
      all_alarms = self.get_pin_alarms(self)
      self.msg(f"deep_sleep(): added {len(all_alarms)} internal alarms")
      all_alarms.extend(alarms)
      self.msg(f"deep_sleep(): added {len(alarms)} from arguments")
      if wakeup:
        all_alarms.append(alarm.time.TimeAlarm(epoch_time=wakeup))
        self.msg("deep_sleep(): added TimeAlarm from argument")

      # test for serial-connection
      if self._connected:
        # this will lead to a fake sleep, so don't preserve
        # button DIOs
        alarm.exit_and_deep_sleep_until_alarms(*all_alarms)

      # else try to create DIOs to preserve state
      # Note: button-wakeup only works with these dios pulled high, but
      #       this is not implmented in mainline CircuitPython
      if self._keypad:
        self._keypad.deinit()
      dios = [DigitalInOut(pin) for pin in self.WAKE_PINS[0]]
      for dio in dios:
        dio.pull = Pull.UP

      # activate deep-sleep
      try:
        # patched version of CircuitPython
        alarm.exit_and_deep_sleep_until_alarms(*all_alarms,
                                               preserve_dios=dios)
      except:
        # mainline: this will not wake up by buttons
        alarm.exit_and_deep_sleep_until_alarms(*all_alarms)
        
    except Exception as ex:
      self.msg(f"could not enter deep-sleep. Exception: {ex}")
      while True:
        time.sleep(1)

  # --- query wake-pin   -----------------------------------------------------

  def get_wake_button(self):
    """ return wake button index or None (e.g. for time-alarm) """

    if self._connected:
      # waking up from fake deep-sleep
      return super().get_wake_button()

    # else query real wake up button
    for index, pin in enumerate(self.WAKE_PINS[0]):
      if board.ON_RESET_PRESSED(pin):
        return index
    return None

impl = HalBadger2350()
