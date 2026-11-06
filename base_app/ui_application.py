# -------------------------------------------------------------------------
# Generic class for e-ink based applications.
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/circuitpython-base-app
# -------------------------------------------------------------------------

# --- imports   -----------------------------------------------------------

import builtins
import time
import board
import gc

import base_app.hal
from settings import secrets, app_config

# --- application class   ----------------------------------------------------

LOG_SRC = "UIApplication"
class UIApplication:

  RED   = [255,0,0]
  GREEN = [0,255,0]

  # --- constructor   --------------------------------------------------------

  def __init__(self,dataprovider,uiprovider, with_rtc=True, with_wifi=True):
    """ constructor """

    self._debug = getattr(app_config, "debug", False)
    # override default logging
    if hasattr(app_config, "logger"):
      self.log = app_config.logger(self)
    self.log(LOG_SRC, f"running on board {board.board_id}")

    # run basic hardware configuration (HAL + hw_config)
    self._setup(with_rtc, with_wifi)  # setup hardware

    blink_time = getattr(self,"led_blink_init",0.1)
    self.blink(blink_time)

    self._dataprovider = dataprovider
    self._dataprovider.set_wifi(self.wifi)
    self._uiprovider = uiprovider
    self.data = {}

  # --- setup attributes from hardware-env   ---------------------------------

  def _setup(self,with_rtc, with_wifi):
    """ setup hardware """

    self.hal = base_app.hal.get_hal(self.log)
    self.hal.debug = self._debug
    if self._debug:
      self.hal.log = self.log

    self.display    = self.hal.display()
    self.is_pygame  = hasattr(self.display,"check_quit")
    self.wifi       = self.hal.wifi()
    if self._debug:
      self.wifi.log = self.log

    if with_rtc:
      self._rtc_ext = self.hal.rtc_ext(
        net_update=getattr(secrets,"net_update",False))
      if self._debug:
        self._rtc_ext.log = self.log
    else:
      self._rtc_ext = None
    gc.collect()

  # --- print debug-message   ------------------------------------------------

  def log_message(self, src, *args):
    """ format a log message """

    header = f"[{time.monotonic():7.2f}][{src}] "
    for arg in args:
      if isinstance(arg, time.struct_time):
        yield header+"%04d-%02d-%02d %02d:%02d:%02d" % (
          arg.tm_year, arg.tm_mon, arg.tm_mday,
          arg.tm_hour, arg.tm_min, arg.tm_sec
          )
      elif isinstance(arg, dict):
        yield f"{header}"+"{"
        for key, value in arg.items():
          yield f"{header}  {key}: {value}"
        yield f"{header}"+"}"
      else:
        yield f"{header}{arg}"

  # --- print debug-message   ------------------------------------------------

  def log(self, src, *args):
    """ print (debug) message """
    if self._debug:
      for line in self.log_message(src, *args):
        print(line)

  # --- blink status-led   ---------------------------------------------------

  def blink(self,duration,color=RED):
    """ blink status-led once for the given duration """
    self.hal.led(1,color=color)
    self.hal.sleep(duration)
    self.hal.led(0,color=color)

  # --- update data from server   --------------------------------------------

  def update_data(self):
    """ update data """

    blink_time = getattr(self,"led_blink_data",0.3)
    self.blink(blink_time,color=UIApplication.RED)
    self.data["bat_level"] = self.hal.bat_level()

    start = time.monotonic()
    self._dataprovider.update_data(self.data)
    duration = time.monotonic()-start
    self.blink(blink_time,color=UIApplication.GREEN)
    self.log(LOG_SRC, f"update_data (dataprovider): {duration:f}s")

  # --- handle data-exception   ----------------------------------------------

  def handle_exception(self,ex):
    """ pass exception of data-provider to ui-provider """

    blink_time = getattr(self,"led_blink_exception",0.6)
    self.blink(blink_time,color=UIApplication.RED)
    start = time.monotonic()
    self.update_display(self._uiprovider.handle_exception(ex, self.data))
    duration = time.monotonic()-start
    self.log(LOG_SRC, f"handle_exception (uiprovider): {duration:f}s")

  # --- create ui   ----------------------------------------------------------

  def create_ui(self):
    """ create UI. UI-provider might buffer UI for performance """

    start = time.monotonic()
    self._uiprovider.create_ui(self.display)
    duration = time.monotonic()-start
    self.log(LOG_SRC, f"create_ui (uiprovider): {duration:f}s")

  # --- free memory from UI   ------------------------------------------------

  def free_ui_memory(self):
    """ free memory used by UI and display """

    if not self.is_pygame:
      self.log(LOG_SRC, f"free memory before clear of UI: {gc.mem_free()}")
      self.display.root_group = None
      self._uiprovider.clear_ui()
      #gc.collect()
      self.log(LOG_SRC, f"free memory after clear of UI: {gc.mem_free()}")

  # --- update display   -----------------------------------------------------

  def update_display(self,content=None):
    """ update display """

    # an explicit content takes precedence. Otherwise
    # update UI with current model and show the returned content
    if not content:
      start = time.monotonic()
      content = self._uiprovider.update_ui(self.data)
      duration = time.monotonic()-start
      self.log(LOG_SRC, f"update_ui (uiprovider): {duration:f}s")

    if not content is None:
      start = time.monotonic()
      self.log(LOG_SRC, f"updating root_group with view (len: {len(content)})")
      self.display.root_group = content  # update root_group ...

      # ... and show content on screen
      if hasattr(self.display,"time_to_refresh"):
        if self.display.time_to_refresh > 0.0:
          # ttr will be >0 only if system is on running on USB-power
          self.log(LOG_SRC, f"waiting for time_to_refresh ({self.display.time_to_refresh})")
          time.sleep(self.display.time_to_refresh)
      try:
        self.log(LOG_SRC, "refreshing...")
        self.display.refresh()
        if hasattr(self.display,"busy"):
          self.log(LOG_SRC, "waiting while busy")
          while self.display.busy:
            time.sleep(0.1)
      except RuntimeError:
        pass
      duration = time.monotonic()-start
      self.log(LOG_SRC, f"update display: {duration:f}s")
    else:
      self.log(LOG_SRC, "no display update")

  # --- shutdown device   ----------------------------------------------------

  def shutdown(self,with_wakeup):
    """ turn off device after setting next wakeup """

    # calculate wakeup time (as struct_time)
    wakeup = None
    if with_wakeup:
      if self._rtc_ext:
        if hasattr(app_config,"time_table"):
          # local time-table overrides application controlled wakeup
          wakeup = self._rtc_ext.get_table_alarm(app_config.time_table)
        elif "sleep_time" in self.data and self.data["sleep_time"]:
          # sleep_time is in seconds, wakeup is a struct_time
          wakeup = self._rtc_ext.get_alarm_time(s=self.data["sleep_time"])
        elif "wake_time" in self.data and self.data["wake_time"]:
          # wake_time should be a valid struct_time
          if isinstance(self.data["wake_time"],int):
            wakeup = time.localtime(self.data["wake_time"])
          else:
            wakeup = self.data["wake_time"]
        else:
          # use fallback run_interval
          wakeup = self._rtc_ext.get_alarm_time(
            s=getattr(app_config, "run_interval", 60))
      else:
        self.log(LOG_SRC, "could not configure wakeup")

    if wakeup is not None:
      # check if wakeup is at least two seconds in the future
      if time.mktime(wakeup)-2 <= time.time():
        # reset at once
        self.log(LOG_SRC, "wakeup is in the past, resetting...")
        self.hal.reset()
      self.log(LOG_SRC, "configuring shutdown/deep-sleep with wakeup at:", wakeup)
    else:
      self.log(LOG_SRC, "shutdown/deep-sleep without wakeup")

    # run shutdown. This could be a noop, so fall back to deep-sleep.
    self.log(LOG_SRC, "trying to shutdown the device")
    self.hal.shutdown(wakeup)
    self.log(LOG_SRC, "falling back to deep-sleep")
    self.hal.deep_sleep(wakeup=time.mktime(wakeup) if wakeup else None)
    return

  # --- cleanup ressources at exit   -----------------------------------------

  def at_exit(self):
    """ cleanup ressources """
    self.hal.at_exit()

  # --- run single execution   -----------------------------------------------

  def run_once(self):
    """ single execution main processing """
    self.run(once=True)

  # --- run at start of run()   ----------------------------------------------

  def run_start(self):
    """ Hook to execute at start of run(). Implement in subclass """
    pass

  # --- run at end of run()   ------------------------------------------------

  def run_end(self):
    """ Hook to execute at end of run(). Implement in subclass """
    pass

  # --- process events (e.g. key-presses)   ----------------------------------

  def process_events(self):
    """ process events while idle. Should be overriden by subclasses.
    Returning True will stop idle-processing.
    """

    # note: calling self.hal.sleep() to give the PyGame-HAL
    #       a chance to check for quit
    self.hal.sleep(0.01)
    return False

  # --- process events for the configured interval   -------------------------

  def run_idle(self):
    """ Override in subclass if necessary """
    interval = getattr(app_config, "run_interval", 1)

    self.log(LOG_SRC, f"running idle for {interval}s")
    while time.monotonic()-self._run_start < interval:
      if self.process_events():
        return

  # --- run   ----------------------------------------------------------------

  def run(self,once=False):
    """ main processing: the subclass has to implement looping """

    self._run_start = time.monotonic()
    try:
      self.run_start()
      self.create_ui()      # ui-provider should buffer this for performance
      self.update_data()
      self.update_display()
      self.run_end()
      success = True
    except Exception as ex1:
      self.log(LOG_SRC, f"failed: {ex1=}")
      if not self._debug:
        # don't show trace on device in debug mode (assume serial connection)
        try:
          self.handle_exception(ex1)
        except Exception as ex2:
          self.log(LOG_SRC, f"failed to handle exception: {ex2=}")
      else:
        import traceback
        try:
          # CircuitPython and CPython > 3.9
          traceback.print_exception(ex1)
        except:
          # CPython prior to 3.10
          traceback.print_exception(None, ex1, ex1.__traceback__)

      # force retry if configured
      success = getattr(app_config, "retry_on_fail", False)

    if once:
      keys = self.hal.keypad()
      if keys and len(keys.events) and self.process_events():
        return                       # subclass consumed a pending key-event
      wakeup = self.shutdown(with_wakeup=success)
    else:
      self.run_idle()
