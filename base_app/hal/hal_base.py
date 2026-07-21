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

class HalBase:
  def __init__(self):
    """ constructor """
    self.debug = False
    self._display = None
    self._wifi = None
    self._keypad = None
    self._rtc_ext = None
    self.BUTTONS = []     # override in subclass
    self.RTC = "NoRTC"    # no external RTC: this will use the builtin RTC

    # expose standard objects from board-module
    for attr in ['DISPLAY', 'LED', 'NEOPIXEL',
                 'I2C', 'SDA', 'SCL',
                 'SPI', 'SCK', 'MOSI', 'MISO',]:
      setattr(self, attr, getattr(board,attr,None))

    # merge methods/attributes from hw_config
    for attr in dir(hw_config):
      if attr[0] != '_':
        setattr(self, attr, getattr(hw_config,attr))

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

  def msg(self,*args):
    """ print debug-message """
    if self.debug:
      print(*args)

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

  def get_wifi(self,debug=False):
    """ return wifi-interface """
    from ..wifi_impl_builtin import WifiImpl
    return WifiImpl(debug=debug)

  def wifi(self,debug=False):
    """ return wifi-interface """
    if not self._wifi:
      self._wifi = self.get_wifi(debug=debug)
    return self._wifi

  def get_display(self, hal):
    """ return display.
    This is typically overriden in a subclass or hw_config for
    boards without internal display.
    """
    return self.DISPLAY

  def display(self):
    """ return display """
    if not self._display:
      self._display = self.get_display(self)
    return self._display

  def get_rtc_ext(self, net_update=False, debug=False):
    """ default implementation: try to create RTC by name """
    try:
      from base_app.rtc_ext.ext_base import ExtBase
      RTC = getattr(self,"RTC","NoRTC")
      if RTC in ["NoRTC", "OsRTC"]:
        # these RTCs don't need the I2C-bus
        try:
          return ExtBase.create(RTC,None,net_update=net_update,debug=debug)
        except Exception as ex2:
          # this is not expected to happen
          self.msg(f"Could not create {RTC}")
          self.msg(f"Reason: {ex2}")
          return None

      if self.I2C:
        self._i2c = self.I2C()
      else:
        import busio
        self._i2c = busio.I2C(self.SCL,self.SDA)
      return ExtBase.create(RTC,self._i2c,net_update=net_update,debug=debug)
    except Exception as ex:
      if debug:
        self.msg(f"Could not create RTC for {RTC}. Falling back to NoRTC.")
        self.msg(f"Reason: {ex}")
      try:
        return ExtBase.create("NoRTC",None,net_update=net_update,debug=debug)
      except Exception as ex3:
        self.msg("Could not create NoRTC")
        self.msg(f"Reason: {ex3}")
      return None

  def rtc_ext(self,net_update=False,debug=False):
    """ return external rtc, if available """
    if not self._rtc_ext:
      self._rtc_ext =  self.get_rtc_ext(net_update=net_update,debug=debug)
    return self._rtc_ext

  def shutdown(self):
    """ shutdown system.
    Needs override in subclass or hw_config
    """
    pass

  def at_exit(self):
    """ exit processing """
    self.msg("hal_base.at_exit()")
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

  def sleep(self,duration):
    """ sleep for the given duration in seconds """
    time.sleep(duration)

  def get_keypad(self, hal):
    """ return configured keypad.
    Needs override in subclass or hw_config
    """
    return None

  def keypad(self):
    """ return configured keypad. """
    if not self._keypad:
      self._keypad = self.get_keypad(self)
    return self._keypad

  def check_key(self,name):
    """ check if key is pressed """

    nr = getattr(self, name, None)
    self.msg(f"check_key({name}): {nr=}")
    if nr is None:
      return False
    keypad = self.keypad()
    if not keypad:
      return False
    queue = keypad.events
    ev = queue.get()
    if ev:
      self.msg(f"check_key({name}): pressed: {ev.pressed}, knr: {ev.key_number}")
      return ev.pressed and ev.key_number == nr
    else:
      self.msg("ckeck_key({name}): empty event-queue")

  def get_pin_alarms(self, hal):
    """ return pin-alarms
    Override in subclass or hw_config if necessary
    """
    if self._keypad:
      self._keypad.deinit()
    import alarm
    alarms = []
    for btn in self.BUTTONS:
      alarms.append(alarm.pin.PinAlarm(btn,value=False,edge=True,pull=True))
    return alarms

  def deep_sleep(self, alarms=[], wakeup=None):
    """ activate deep-sleep.
    The default merges all alarms passed as arguments with
    pin-alarms defined via get_pin_alarms().
    """
    try:
      import alarm
      all_alarms = self.get_pin_alarms(self)
      all_alarms.extend(alarms)
      if wakeup:
        all_alarms.append(alarm.time.TimeAlarm(epoch_time=wakeup))
    except:
      while True:
        time.sleep(1)

  def nvram_read(self, offset, count):
    """ read data from nvram """
    import microcontroller
    if not microcontroller.nvm:
      raise NotImplementedError("nvram not available for this platform")
    return microcontroller.nvm[offset:offset+count]

  def nvram_write(self, offset, data):
    """ write data to nvram """
    import microcontroller
    if not microcontroller.nvm:
      raise NotImplementedError("nvram not available for this platform")
    microcontroller.nvm[offset:offset+len(data)] = data
