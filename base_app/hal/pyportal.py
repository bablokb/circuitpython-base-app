# ----------------------------------------------------------------------------
# pyportal.py: HAL for Adafruit PyPortal
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/circuitpython-base-app
# ----------------------------------------------------------------------------

import board

from digitalio import DigitalInOut, Direction

from .hal_base import HalBase

class HalPyPortal(HalBase):
  """ PyPortal specific HAL-class """

  def _init_led(self):
    """ use LED instead of Neopixel (the PyPortal has both) """
    if not hasattr(self,"_led"):
      self._led = DigitalInOut(board.LED)
      self._led.direction = Direction.OUTPUT

impl = HalPyPortal()
