# ----------------------------------------------------------------------------
# adafruit_magtag_2_9_grayscale.py: board-specific setup for Magtag
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/circuitpython-base-app
# ----------------------------------------------------------------------------

import board
from analogio import AnalogIn
from digitalio import DigitalInOut, Direction

import neopixel

from .hal_base import HalBase

class HalMagtag(HalBase):
  """ Magtag specific HAL-class """

  def __init__(self):
    """ constructor """
    super().__init__()
    self.eink = True
    self.gamut = "gray_4"
    # BUTTONS is empty in super-class, but might be tweaked in hw_config
    if not getattr(self,"BUTTONS",None):
      # format is ([pin, ...], value, pull)
      # left to right: left,       up,        down,      right
      self.BUTTONS = ([board.D15, board.D14, board.D12, board.D11],
                      False, True)
    if not getattr(self,"WAKE_PINS",None):
      # format is ([pin, ...], value, edge, pull)
      # use left and right for deep-sleep alarm buttons
      self.WAKE_PINS = ([board.D15, board.D11],
                        False, False, True)

  def bat_level(self):
    """ return battery level """
    from analogio import AnalogIn
    adc = AnalogIn(board.BATTERY)
    level = (adc.value / 65535.0) * 3.3 * 2
    adc.deinit()
    return level

impl = HalMagtag()
