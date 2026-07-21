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

  def __init__(self):
    """ constructor """
    super().__init__()
    self.LED = board.USER_LED
    self.eink = False
    self.gamut = "rgb16"
    # BUTTONS is empty in super-class, but might be tweaked in hw_config
    if not getattr(self,"BUTTONS",[]):
      self.BUTTONS = [board.SW_A, board.SW_B, board.SW_C,
                      board.SW_UP, board.SW_DOWN]

  def get_keypad(self, hal):
    """ return configured keypad """
    import keypad
    return keypad.Keys(self.BUTTONS,
                       value_when_pressed=True, pull=True,
                       interval=0.1,max_events=4
    )

impl = HalTufty2040()
