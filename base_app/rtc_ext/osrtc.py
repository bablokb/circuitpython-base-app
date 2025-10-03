#-----------------------------------------------------------------------------
# Fake external and internal RTC with system-clock. This will allow the
# RTC update-logic also work for the generic linux HAL.
# RTC present).
#
# Author: Bernhard Bablok
#
# Website: https://github.com/bablokb/circuitpython-base-app
#-----------------------------------------------------------------------------

import time
from .ext_base import ExtBase

# --- class NoRTC   ----------------------------------------------------------

class NoRTC(ExtBase):

  # --- constructor   --------------------------------------------------------

  def __init__(self,i2c,wifi=None,net_update=False):
    """ constructor """

    super().__init__(self,rtc_int=self,wifi=wifi,net_update=net_update)

  # --- check power-state   --------------------------------------------------

  def _lost_power(self):
    """ check for power-loss: assume always powered """
    return False

  # --- facade for datetime   ------------------------------------------------

  @property
  def datetime(self) -> time.struct_time:
    return time.localtime()

  @datetime.setter
  def datetime(self, value: struct_time):
    """ we don't set the system-time from an application program """
    pass
