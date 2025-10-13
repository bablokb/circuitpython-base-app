# -------------------------------------------------------------------------
# UI-provider for the template application.
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/circuitpython-base-app
# -------------------------------------------------------------------------

import gc
import displayio
import time
import terminalio
import vectorio

from adafruit_display_text import label

from settings import secrets, hw_config, app_config
from ui_settings import UI_PALETTE, COLOR

# --- main data-provider class   ---------------------------------------------

class UIProvider:

  def __init__(self):
    self._debug   = getattr(app_config, "debug", False)
    self._display = None
    self._view    = None

  # --- print debug-message   ------------------------------------------------

  def msg(self,text):
    """ print (debug) message """
    if self._debug:
      print(text)

  # --- create complete content   --------------------------------------------

  def create_ui(self,display):
    """ create content """

    if self._view:
      return

    # save display
    self._display = display
    w2 = int(display.width/2)
    h2 = int(display.height/2)
    # text label for time
    self._time_txt = label.Label(terminalio.FONT,
                                 text='00:00:00',
                                 color=UI_PALETTE[COLOR.BLUE],
                                 scale=3,
                                 anchor_point=(0.5,0.5),
                                 anchored_position=(w2,h2))

    # background circle for time
    circle = vectorio.Circle(pixel_shader=UI_PALETTE,
                             radius=int(0.8*min(w2,h2)),
                             x=w2, y=h2)
    circle.color_index=COLOR.YELLOW

    # add objects to group
    self._view = displayio.Group()
    self._view.append(circle)
    self._view.append(self._time_txt)

  # --- update ui   ----------------------------------------------------------

  def update_ui(self,data):
    """ update data: callback for Application """

    # pretty-print time
    t = time.localtime(data["epoch"])
    if getattr(app_config,"full",False):
      self._time_txt.text = f"{t.tm_hour:02d}:{t.tm_min:02d}:{t.tm_sec:02d}"
    else:
      self._time_txt.text = f"{t.tm_hour:02d}:{t.tm_min:02d}"
    return self._view

  # --- clear UI and free memory   -------------------------------------------

  def clear_ui(self):
    """ clear UI """

    if self._view:
      for _ in range(len(self._view)):
        self._view.pop()
    self._view = None
    gc.collect()

  # --- handle exception   ---------------------------------------------------

  def handle_exception(self,ex):
    """ handle exception """

    import traceback
    try:
      # CircuitPython and CPython > 3.9
      ex_txt = ''.join(traceback.format_exception(ex))
    except:
      # CPython prior to 3.10
      ex_txt = ''.join(traceback.format_exception(None, ex, ex.__traceback__))

    # print to console
    print(60*'-')
    print(ex_txt)
    print(60*'-')

    # and update display
    if not self._display:
      return

    error_txt = label.Label(terminalio.FONT,
                            text=ex_txt,
                            color=UI_PALETTE[COLOR.RED],
                            line_spacing=1.2,
                            anchor_point=(0,0),
                            anchored_position=(0,0))

    g = displayio.Group()
    g.append(error_txt)
    return g
