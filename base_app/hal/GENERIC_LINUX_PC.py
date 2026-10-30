# ----------------------------------------------------------------------------
# GENERIC_LINUX_PC.py: HAL for simulation with PygameDisplay
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/circuitpython-base-app
# ----------------------------------------------------------------------------

import board
import sys
import os
import time

import socket
import ssl
import adafruit_requests

from .hal_base import HalBase

from settings import app_config

class WifiImpl:
  """ request-implementation using sockets from CPython """

  def __init__(self,debug=False):
    """ constructor """
    self.debug = debug
    self._requests = None

  def get(self,url):
    return self.requests.get(url)

  @property
  def requests(self):
    """ return requests-object """
    if not self._requests:
      self._requests = adafruit_requests.Session(socket,
                                                 ssl.create_default_context())
    return self._requests

  @property
  def pool(self):
    """ for CPython, the socket-module is the pool-object """
    return socket

  @property
  def radio(self):
    """ return ourselves as radio """
    return self

  @property
  def mac_address(self):
    """ emulate radio.mac_address """
    mac = None
    try:
      for d in sorted(os.listdir("/sys/class/net/")):
        if d == "lo":
          continue
        with open(f"/sys/class/net/{d}/address") as a:
          mac = a.readline()[:-1]
          if mac != "00:00:00:00:00:00":
            break
    except:
      pass
    return mac

  @property
  def connected(self):
    """ emulate radio.connected """
    return True

  def connect(self):
    """ noop - we assume we are always connected """
    pass

class HalPygame(HalBase):
  """ GENERIC_LINUX_PC specific HAL-class """

  def __init__(self):
    """ constructor """

    self._wake_pin = None
    # set the defaults here first, because ...
    self.eink = False
    self.gamut = "rgb16"
    # the super constructor merges hw_config which might override these
    super().__init__()
    if self.RTC is None or self.RTC == "NoRTC":
      self.RTC = "OsRTC"                          # use OS-internal RTC

  def bat_level(self):
    """ return battery level """
    return 3.6

  def led(self,value,color=None):
    """ set status LED (not-supported)"""
    pass

  def get_wifi(self,debug=False):
    """ return wifi-interface """
    return WifiImpl(debug=debug)

  def shutdown(self, wakeup):
    """ process shutdown request.

    Since PyGame does not support 'hardware'-shutdown, this
    is a noop. To emulate shutdown, set
      hw_config.shutdown_emulate=True.

    To keep the display visible for a while, set
      hw_config.shutdown_delay = <n_secs>

    wakeup is ignored.
    """

    if not getattr(self, "shutdown_emulate", False):
      # noop
      self.msg(f"{board.board_id}: shutdown() is a noop")
      return
    delay = getattr(self, "shutdown_delay", 0)
    self.msg(f"emulating shutdown after waiting {delay}s")
    self.sleep(delay)
    sys.exit(0)

  def sleep(self,duration):
    if not self._display:
      super().sleep(duration)
      return

    start = time.monotonic()
    while time.monotonic()-start < duration:
      if self._display.check_quit():
        sys.exit(0)

  def get_keypad(self, hal):
    """ return configured keypad. """
    if self.BUTTONS and self._display:
      return self._display.keypad(self.BUTTONS[0],
                                  value_when_pressed=self.BUTTONS[1],
                                  pull=self.BUTTONS[2],
                                  interval=0,max_events=4
                                  )
    return None

  def deep_sleep(self,alarms=[], wakeup=None):
    """ activate deep-sleep.

    This will wait until wakeup is due, and then restart the
    program.
    """

    if not wakeup:
      wakeup = sys.maxsize

    if not self._display:
      while time.time() < wakeup:
        time.sleep(1)
    else:
      wake_pins = getattr(self, "WAKE_PINS", None)
      if self._keypad and wake_pins:
        # deinit standard keypad and create a new keypad for wake-pins
        self._keypad.deinit()
        self._keypad = self._display.keypad(
          wake_pins[0],
          value_when_pressed=wake_pins[1],
          pull=wake_pins[3],
          interval=0,max_events=4
          )

      keys = self.keypad()
      self.msg(f"{board.board_id}: deep-sleep()" +
               f"{' with wake keys' if keys else ''}")
      while time.time() < wakeup:
        if self._display.check_quit():
          sys.exit(0)
        if keys:
          ev = keys.events.get()
          if ev and ev.pressed:
            self._wake_pin = ev.key_number
            break
        time.sleep(0.1)
    self.reset()

  def get_appdir(self):
    """ query application directory """
    appdir = os.path.join(os.path.expanduser('~'),
                         ".local","share",app_config.app_name)
    os.makedirs(appdir, mode=0o700, exist_ok=True)
    return appdir

  def get_nvram(self):
    """ return emulated nvram storage-location """
    return os.path.join(self.get_appdir(),"nvram.data")

  def nvram_read(self, offset, count):
    """ emulate reading data from nvram """
    result = bytearray(count)
    nvram = self.get_nvram()
    if not os.path.exists(nvram):
      return result
    with open(nvram,"rb") as f:
      f.seek(offset)
      data = f.read(count)
    result[:len(data)] = data
    return result

  def nvram_write(self, offset, data):
    """ emulating write data to nvram """
    with open(self.get_nvram(),"wb") as f:
      f.seek(offset)
      f.write(data)

  def reset(self):
    """ emulate reset device """
    sys.stdout.flush()
    sys.stderr.flush()
    args = [sys.executable, "./main.py"]
    if not self._wake_pin is None:
      args.append(f"{self._wake_pin}")
    self.msg(f"{board.board_id}: reset(): exec {' '.join(args)}")
    os.execv(sys.executable, args)

  def start_code_file(self,name):
    """ emulate supervisor.set_next_code_file()+supervisor.reload() """
    self.msg(
      f"{board.board_id}: starting '{sys.executable} {name}'")
    sys.stdout.flush()
    sys.stderr.flush()
    os.execv(sys.executable, [sys.executable, name])

  def get_wake_button(self):
    """ return wake button index or None (e.g. for time-alarm) """
    return int(sys.argv[1]) if len(sys.argv) > 1 else None

impl = HalPygame()
