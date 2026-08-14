# ----------------------------------------------------------------------------
# GENERIC_LINUX_PC.py: HAL for simulation with PygameDisplay
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/circuitpython-base-app
# ----------------------------------------------------------------------------

import sys
import os
import time

import socket
import adafruit_requests

from .hal_base import HalBase

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
      self._requests = adafruit_requests.Session(socket)
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

    # set the defaults here first, because ...
    self.eink = False
    self.gamut = "rgb16"
    # the super constructor merges hw_config which might override these
    super().__init__()
    if self.RTC is None:
      self.RTC = "OsRTC"    # use OS-internal RTC

  def bat_level(self):
    """ return battery level """
    return 3.6

  def led(self,value,color=None):
    """ set status LED (not-supported)"""
    pass

  def get_wifi(self,debug=False):
    """ return wifi-interface """
    return WifiImpl(debug=debug)

  def shutdown(self):
    """ leave program (here: wait for quit) """
    if not self._display:
      sys.exit(0)
    else:
      self.deep_sleep()

  def sleep(self,duration):
    if not self._display:
      super.sleep(duration)
      return

    start = time.monotonic()
    while time.monotonic()-start < duration:
      if self._display.check_quit():
        sys.exit(0)

  def check_key(self,name):
    """ check if key is pressed (currently not supported) """
    return False

  def deep_sleep(self,alarms=[], wakeup=None):
    """ activate deep-sleep (not supported, fall back to idle) """

    if not self._display:
      while True:
        time.sleep(1)

    while True:
      if self._display.check_quit():
        sys.exit(0)

  def get_nvram(self):
    """ return emulated nvram storage-location """
    import os
    from settings import app_config
    nvram = os.path.join(os.path.expanduser('~'),
                         ".local","share",app_config.app_name)
    os.makedirs(nvram, mode=0o700, exist_ok=True)
    return os.path.join(nvram,"nvram.data")

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

impl = HalPygame()
