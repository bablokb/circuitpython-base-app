# ----------------------------------------------------------------------------
# HalBase: Hardware-Abstraction-Layer base-class.
#
# This class implements standard methods. If necessary, some of them must be
# overridden by board-specific sub-classes.
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/circuitpython-base-app
# ----------------------------------------------------------------------------

import board
import time
from digitalio import DigitalInOut, Direction

try:
  from settings import hw_config
except:
  class Settings:
    pass
  hw_config = Settings()

LOG_SRC = "HalBase"
class HalBase:

  # --- constructor   ----------------------------------------------------------

  def __init__(self):
    """ constructor """
    self.debug = False
    self._display = None
    self._wifi = None
    self._keypad = None
    self._rtc_ext = None
    self.BUTTONS = None     # ([pin, ...], value, pull)
    self.WAKE_PINS = None   # ([pin, ...], value, edge, pull)
    self.RTC = None

    # expose standard objects from board-module
    for attr in ['DISPLAY', 'LED', 'NEOPIXEL',
                 'I2C', 'SDA', 'SCL',
                 'SPI', 'SCK', 'MOSI', 'MISO',]:
      setattr(self, attr, getattr(board,attr,None))

    # merge methods/attributes from hw_config
    for attr in dir(hw_config):
      if attr[0] != '_':
        setattr(self, attr, getattr(hw_config,attr))

    # run init() (override in hw_config)
    self.init(self)

  # --- initialization   -------------------------------------------------------

  def init(self, hal):
    """ generic initialization. Must be overriden in hw_config """
    pass

  # --- initialize LED/neopixel   ----------------------------------------------

  def _init_led(self):
    """ initialize LED/Neopixel """
    if hasattr(self,'_led') or hasattr(self,'_pixel'):
      return
    if self.NEOPIXEL:
      if not hasattr(self,'_pixel'):
        if hasattr(board,'NEOPIXEL_POWER'):
          # need to do this first,
          # https://github.com/adafruit/Adafruit_CircuitPython_MagTag/issues/75
          self._pixel_poweroff = DigitalInOut(board.NEOPIXEL_POWER)
          self._pixel_poweroff.direction = Direction.OUTPUT
        import neopixel
        self._pixel = neopixel.NeoPixel(board.NEOPIXEL,1,
                                        brightness=0.1,auto_write=False)
    else:
      led = self.LED
      if led and not hasattr(self,'_led'):
        self._led = DigitalInOut(led)
        self._led.direction = Direction.OUTPUT

  # --- print debug-message   ------------------------------------------------

  def log(self, src, *args):
    """ print (debug) message. Override from application """
    pass

  # --- set LED   --------------------------------------------------------------

  def led(self,value,color=[255,0,0]):
    """ set status LED/Neopixel """
    self._init_led()
    if hasattr(self,'_pixel'):
      if hasattr(self,'_pixel_poweroff'):
        self._pixel_poweroff.value = not value
      if value:
        self._pixel.fill(color)
        self._pixel.show()
      elif not hasattr(self,'_pixel_poweroff'):
        self._pixel.fill(0)
        self._pixel.show()
    elif hasattr(self,'_led'):
      self._led.value = value

  # --- query battery level   --------------------------------------------------

  def bat_level(self):
    """ return battery level """
    if hasattr(board,"VOLTAGE_MONITOR"):
      from analogio import AnalogIn
      adc = AnalogIn(board.VOLTAGE_MONITOR)
      level = adc.value *  3 * 3.3 / 65535
      adc.deinit()
      return level
    else:
      return 0.0

  # --- return wifi-implementation (factory)   ---------------------------------

  def get_wifi(self):
    """ return wifi-interface """
    from ..wifi_impl_builtin import WifiImpl
    return WifiImpl()

  # --- return wifi-instance   -------------------------------------------------

  def wifi(self):
    """ return wifi-interface """
    if not self._wifi:
      self._wifi = self.get_wifi()
    return self._wifi

  # --- return display (factory)   ---------------------------------------------

  def get_display(self, hal):
    """ return display.
    This is typically overriden in a subclass or hw_config for
    boards without internal display.
    """
    return self.DISPLAY

  # --- return display-instance   ----------------------------------------------

  def display(self):
    """ return display """
    if not self._display:
      self._display = self.get_display(self)
    return self._display

  # --- return external RTC (factory)   ----------------------------------------

  def get_rtc_ext(self, net_update=False):
    """ default implementation: try to create RTC by name """
    try:
      from base_app.rtc_ext.ext_base import ExtBase
      _rtc = getattr(self,"RTC", None)
      if _rtc is None:
        _rtc = "NoRTC"
      if _rtc in ["NoRTC", "OsRTC"]:
        # these RTCs don't need the I2C-bus
        try:
          return ExtBase.create(_rtc,None,net_update=net_update)
        except Exception as ex2:
          # this is not expected to happen
          self.log(LOG_SRC, f"Could not create {_rtc}")
          self.log(LOG_SRC, f"Reason: {ex2}")
          return None

      if self.I2C:
        self._i2c = self.I2C()
      else:
        import busio
        self._i2c = busio.I2C(self.SCL,self.SDA)
      return ExtBase.create(_rtc,self._i2c,net_update=net_update)
    except Exception as ex:
      self.log(LOG_SRC, f"Could not create RTC for {RTC}. Falling back to NoRTC.")
      self.log(LOG_SRC, f"Reason: {ex}")
      try:
        return ExtBase.create("NoRTC",None,net_update=net_update)
      except Exception as ex3:
        self.log(LOG_SRC, "Could not create NoRTC")
        self.log(LOG_SRC, f"Reason: {ex3}")
      return None

  # --- return external RTC-instance   -----------------------------------------

  def rtc_ext(self,net_update=False):
    """ return external rtc, if available """
    if not self._rtc_ext:
      self._rtc_ext =  self.get_rtc_ext(net_update=net_update)
    return self._rtc_ext

  # --- update RTCs (internal and external)   ----------------------------------

  def update_rtc(self, ts):
    """ update internal and external RTC.
    ts: timestamp in unix-time or struct_time
        If None, update from a time-server (worldtimeapi protocol)
    """
    if self.RTC == "OsRTC":   # skip OS-level rtc
      return
    rtc_ext = self.rtc_ext()
    rtc_ext.update(new_time=ts)

  # --- shutdown with optional wakeup   ----------------------------------------

  def shutdown(self, wakeup):
    """ shutdown system.
    Needs override in subclass or hw_config
    """
    pass

  # --- add at-exit processing   -----------------------------------------------

  def at_exit(self):
    """ exit processing """
    self.log(LOG_SRC, "hal_base.at_exit()")
    try:
      if not hasattr(board,"DISPLAY"):
        import displayio
        displayio.release_displays()
    except:
      pass
    try:
      self._keypad.deinit()
    except:
      pass
    try:
      self._i2c.deinit()
    except:
      pass

  # --- sleep   ----------------------------------------------------------------

  def sleep(self,duration):
    """ sleep for the given duration in seconds """
    time.sleep(duration)

  # --- return keypad (factory)   ----------------------------------------------

  def get_keypad(self, hal):
    """ return configured keypad. """
    if self.BUTTONS:
      import keypad
      return keypad.Keys(self.BUTTONS[0],
                         value_when_pressed=self.BUTTONS[1],
                         pull=self.BUTTONS[2],
                         interval=0.1,max_events=4
                         )
    return None

  # --- return keypad-instance   -----------------------------------------------

  def keypad(self):
    """ return configured keypad. """
    if not self._keypad:
      self._keypad = self.get_keypad(self)
    return self._keypad

  # --- return next pending key event   ----------------------------------------

  def get_key_event(self, ignore_released=True):
    """ return next key event. This does not return an object of type
    keypad.Event, but a tuple (key_number, event) to allow
    subclasses to manipulate the key-number before returning them.
    """

    keys = self.keypad()
    if not keys:                 # no keypad defined
      return None
    ev = keys.events.get()
    while ev:
      if ignore_released and ev.released:    # skip release events
        ev = keys.events.get()
        continue
      return (ev.key_number, ev)
    return None                   # no pending button event

  # --- return pin-alarms   ----------------------------------------------------

  def get_pin_alarms(self, hal):
    """ return pin-alarms
    Override in subclass or hw_config if necessary
    """
    if self._keypad:
      self._keypad.deinit()
    import alarm
    alarms = []
    # use self.WAKE_PINS if available, else fall back to self.BUTTONS
    wake_pins = getattr(self, "WAKE_PINS", None)
    buttons   = getattr(self, "BUTTONS", None)
    if wake_pins:
      alarm_pins, value, edge, pull = wake_pins
    elif buttons:
      alarm_pins, value, pull = buttons
      edge = False
    else:
      alarm_pins = []
    for pin in alarm_pins:
      alarms.append(alarm.pin.PinAlarm(pin,
                                       value=value, edge=edge, pull=pull))
    return alarms

  # --- enter deep-sleep   -----------------------------------------------------

  def deep_sleep(self, alarms=[], wakeup=None):
    """ activate deep-sleep.
    The default merges all alarms passed as arguments with
    pin-alarms defined via get_pin_alarms().
    """
    try:
      import alarm
      all_alarms = self.get_pin_alarms(self)
      self.log(LOG_SRC, f"deep_sleep(): added {len(all_alarms)} internal alarms")
      all_alarms.extend(alarms)
      self.log(LOG_SRC, f"deep_sleep(): added {len(alarms)} from arguments")
      if wakeup:
        all_alarms.append(alarm.time.TimeAlarm(epoch_time=wakeup))
        self.log(LOG_SRC, f"deep_sleep(): added TimeAlarm from argument")
      alarm.exit_and_deep_sleep_until_alarms(*all_alarms)
    except Exception as ex:
      self.log(LOG_SRC, f"could not enter deep-sleep. Exception: {ex}")
      while True:
        time.sleep(1)

  # --- read NVRAM   -----------------------------------------------------------

  def nvram_read(self, offset, count):
    """ read data from nvram """
    import microcontroller
    if not microcontroller.nvm:
      raise NotImplementedError("nvram not available for this platform")
    return microcontroller.nvm[offset:offset+count]

  # --- write NVRAM   ----------------------------------------------------------

  def nvram_write(self, offset, data):
    """ write data to nvram """
    import microcontroller
    if not microcontroller.nvm:
      raise NotImplementedError("nvram not available for this platform")
    microcontroller.nvm[offset:offset+len(data)] = data

  # --- reset device   ---------------------------------------------------------

  def reset(self):
    """ reset device """
    import microcontroller
    microcontroller.reset()

  # --- restart with given code-file   -----------------------------------------

  def start_code_file(self, name):
    """ emulate supervisor.set_next_code_file()+supervisor.reload() """
    import supervisor
    supervisor.set_next_code_file(name)
    supervisor.reload()

  # --- query wake button   ----------------------------------------------------

  def get_wake_button(self):
    """ return wake button index or None (e.g. for time-alarm) """

    try:
      import alarm
      if type(alarm.wake_alarm) != alarm.pin.PinAlarm:
        return None
      # use self.WAKE_PINS if available, else fall back to self.BUTTONS
      wake_pins = getattr(self, "WAKE_PINS", None)
      buttons   = getattr(self, "BUTTONS", None)
      if wake_pins:
        alarm_pins = wake_pins[0]
      elif buttons:
        alarm_pins = buttons[0]
      else:
        return None

      # test sequentially
      self.log(LOG_SRC, f"get_wake_button(): wake pin: {alarm.wake_alarm.pin}")
      for index, pin in enumerate(alarm_pins):
        if pin == alarm.wake_alarm.pin:
          self.log(LOG_SRC, f"get_wake_button(): found pin at index {index}")
          return index
      # no hit
      return None
    except Exception as ex:
      # typically no alarm module
      self.log(LOG_SRC, f"get_wake_button(): could not query wake-button: {ex}")
      return None
