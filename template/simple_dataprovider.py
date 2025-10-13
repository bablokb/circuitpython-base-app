# -------------------------------------------------------------------------
# Dataprovider for the template application.
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/circuitpython-base-app
# -------------------------------------------------------------------------

import time
from settings import secrets, hw_config, app_config

# --- main data-provider class   ---------------------------------------------

class DataProvider:

  def __init__(self):
    self._debug = getattr(app_config, "debug", False)
    self._wifi  = None

  # --- print debug-message   ------------------------------------------------

  def msg(self,text):
    """ print (debug) message """
    if self._debug:
      print(text)

  # --- set wifi-object   ----------------------------------------------------

  def set_wifi(self,wifi):
    """ set wifi-object """
    self._wifi = wifi

  # --- query departures   ---------------------------------------------------

  def update_data(self,data):
    """ callback for App: query data and update data-object """

    # this simple dataprovider just sets the epoch-time
    data["epoch"] = time.time()
