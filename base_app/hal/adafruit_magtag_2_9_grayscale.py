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
    if not getattr(self,"BUTTONS",[]):
      self.BUTTONS = [board.D14,board.D12,board.D15,board.D11]

  def bat_level(self):
    """ return battery level """
    from analogio import AnalogIn
    adc = AnalogIn(board.BATTERY)
    level = (adc.value / 65535.0) * 3.3 * 2
    adc.deinit()
    return level

  def get_keypad(self, hal):
    """ return configured keypad """
    import keypad
    return keypad.Keys(self.BUTTONS,
      value_when_pressed=False,pull=True,
      interval=0.1,max_events=4
      )

impl = HalMagtag()
