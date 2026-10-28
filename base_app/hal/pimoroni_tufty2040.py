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
    if not getattr(self,"BUTTONS",None):
      self.BUTTONS = ([board.SW_A, board.SW_B, board.SW_C,
                       board.SW_UP, board.SW_DOWN],
                      True, True)
    if not getattr(self,"button_names",None):
      self.button_names = ["A", "B", "C", "up", "down"]
    if not getattr(self,"WAKE_PINS",None):
      # format is ([pin, ...], value, edge, pull)
      self.WAKE_PINS = ([board.SW_A, board.SW_B, board.SW_C,
                         board.SW_UP, board.SW_DOWN],
                        True, False, True)
    if not getattr(self,"w_button_names",None):
      self.w_button_names = ["A", "B", "C", "up", "down"]

impl = HalTufty2040()
