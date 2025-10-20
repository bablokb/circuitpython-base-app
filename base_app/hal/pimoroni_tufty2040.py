# ----------------------------------------------------------------------------
# pimoroni_tufty2040.py: HAL for Pimoroni Tufty2040
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/circuitpython-base-app
# ----------------------------------------------------------------------------

import board

from digitalio import DigitalInOut, Direction

from .hal_base import HalBase

class HalTufty2040(HalBase):
  """ Tufty2040 specific HAL-class """

  def _init_led(self):
    """ initialize LED/Neopixel """
    if not hasattr(self,"_led"):
      self._led = DigitalInOut(board.USER_LED)
      self._led.direction = Direction.OUTPUT

  def get_keypad(self):
    """ return configured keypad """

    if not self._keypad:
      import keypad
      self._keypad = keypad.Keys(
        [board.SW_A, board.SW_B, board.SW_C, board.SW_UP, board.SW_DOWN],
        value_when_pressed=True, pull=True,
        interval=0.1,max_events=4
      )
    return self._keypad

impl = HalTufty2040()
