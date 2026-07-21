# ----------------------------------------------------------------------------
# picow_pi_base_rev1.py: HAL for Pico Pi Base, pcb-en-control
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/circuitpython-base-app
# ----------------------------------------------------------------------------

import board
from digitalio import DigitalInOut, Direction

from .hal_base import HalBase

DONE_PIN  = board.GP4

class HalPicoPiBase(HalBase):
  """ pico-pi-base specific HAL-class """

  def __init__(self):
    """ constructor """
    super().__init__()
    self._done           = DigitalInOut(DONE_PIN)
    self._done.direction = Direction.OUTPUT
    self._done.value     = 0
    self.RTC             = "PCF8563"

  def shutdown(self):
    """ turn off power by pulling GP4 high """
    self.msg("HalPicoPiBase.shutdown() started")
    self._done.value = 1
    time.sleep(0.2)
    self._done.value = 0
    time.sleep(0.5)

impl = HalPicoPiBase()
