# ----------------------------------------------------------------------------
# Template main.py for base-application.
#
# This template application will show the current time on a display.
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/circuitypthon-base-app
# ----------------------------------------------------------------------------

# --- imports   --------------------------------------------------------------

import time
import atexit

from settings import app_config
from base_app.ui_application import UIApplication
from simple_dataprovider import DataProvider
from simple_uiprovider import UIProvider

# --- wait for connected console   -------------------------------------------

def wait_for_console(duration=5):
  """ wait for serial connection.
  If there is no supervisor, we are on CPython and don't have to wait.
  """
  import board
  try:
    import supervisor
    import time
    elapsed = time.monotonic() + duration
    while (not supervisor.runtime.serial_connected and
           time.monotonic() < elapsed):
      time.sleep(1)
  except:
    pass
  print(f"running on board {board.board_id}")

# --- cleanup at exit   ------------------------------------------------------

def at_exit(app):
  app.at_exit()

# --- application class with overrides   --------------------------------------

class App(UIApplication):
  """ class App """
  def __init__(self,*args,**kwargs):
    super().__init__(*args, ** kwargs)

  # --- more overrides   ------------------------------------------------------


# --- main program   ----------------------------------------------------------

if getattr(app_config,"debug",False):
  wait_for_console()

start = time.monotonic()
data_provider = DataProvider()
ui_provider = UIProvider()

app = App(data_provider,ui_provider,with_rtc=True)
atexit.register(at_exit,app)

if getattr(app_config,"debug",False):
  print(f"startup: {time.monotonic()-start:f}s")

while True:
  app.run()

# or in case of single-shot applications (e.g. for e-ink displays):
# app.run_once()
