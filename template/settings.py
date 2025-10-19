# ----------------------------------------------------------------------------
# settings.py: template for secrets, hw_config and app_config
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/circuitpython-base-app
# ----------------------------------------------------------------------------

class Settings:
  pass

# network configuration   ----------------------------------------------------

secrets = Settings()
secrets.ssid      = 'my-ssid'
secrets.password  = 'my-secret-password'
secrets.retry     = 2
secrets.debugflag = False
secrets.channel   = 6
secrets.timeout   = 10
secrets.time_url = 'http://worldtimeapi.org/api/ip'
secrets.net_update = True

# app configuration   --------------------------------------------------------

# generic
app_config = Settings()
app_config.debug = True
app_config.run_interval = 5

# application specific (this is for simple_uiprovider.py)
app_config.full = True           # full: show time as hh:mm:ss, else hh:mm

# hardware configuration   ---------------------------------------------------
# this is an example for a ST7789-display with 320x240 pixel

import atexit
import board
import busio
import displayio
import fourwire

from adafruit_bus_device.i2c_device import I2CDevice
from adafruit_st7789 import ST7789

# --- basic display configuration   ------------------------------------------

WIDTH      = 320
HEIGHT     = 240
ROTATION   = 90
BRIGHTNESS = 0.8
DRIVER     = ST7789

# --- hardware-pins   --------------------------------------------------------

SDA_PIN   = board.GP26
SCL_PIN   = board.GP27

SCK_PIN   = board.GP10
MOSI_PIN  = board.GP11
MISO_PIN  = board.GP12

DC_PIN    = board.GP8
RST_PIN   = board.GP15
CS_PIN    = board.GP9
BL_PIN    = board.GP13

LED_PIN   = board.LED

# --- atexit processing   ----------------------------------------------------

def at_exit(spi):
  """ release spi """
  spi.deinit()

# --- display-factory method   ------------------------------------------------

def _get_display(hal):
  """ create display with configured driver """

  displayio.release_displays()
  spi = busio.SPI(SCK_PIN,MOSI=MOSI_PIN,MISO=MISO_PIN)
  atexit.register(at_exit,spi)
  display_bus = fourwire.FourWire(
    spi, command=DC_PIN, chip_select=CS_PIN, reset=RST_PIN, baudrate=40_000_000
  )
  display = DRIVER(display_bus, width=WIDTH, height=HEIGHT, rotation=ROTATION,
                   brightness=BRIGHTNESS, backlight_pin=BL_PIN,)
  return display

# --- keypad factory method   ------------------------------------------------

def _get_keypad(hal):
  """ return keypad-object. """
  #import keypad
  #kp = keypad.Keys(
  #  [board.SW_A, board.SW_B, board.SW_C, board.SW_UP, board.SW_DOWN],
  #  value_when_pressed=True,pull=True,
  #  interval=0.1,max_events=4
  #  )
  #return kp

# --- RTC factory method   ---------------------------------------------------

def _get_rtc_ext(net_update=net_update,debug=debug):
  """ for a non-standard RTC. See rtc_ext/pcf8523.py for an example """
  pass

# --- wifi factory method   --------------------------------------------------

def _get_wifi(hal,debug=False):
  """ for a non-standard wifi implementation """
  pass

# --- deep-sleep method   ----------------------------------------------------

def _deep_sleep(alarms=[]):
  """ for a non-standard deep-sleep implementation """
  pass

# hardware configuration   ---------------------------------------------------

hw_config     = Settings()
hw_config.LED = LED_PIN
hw_config.SDA = SDA_PIN
hw_config.SCL = SCL_PIN

# use factory methods (only set when implemented)
hw_config.DISPLAY      = _get_display
hw_config.RTC          = "PCF8523"               # for standard RTCs in rtc_ext/
#hw_config.get_rtc_ext = _get_rtc_ext
#hw_config.get_keypad  = _get_keypad
#hw_config.get_wifi    = _get_wifi
#hw_config.deep_sleep  = _deep_sleep

# default blink durations
#hw_config.led_blink_init      = 0.1
#hw_config.led_blink_power_off = 0.1
#hw_config.led_blink_data      = 0.3
#hw_config.led_blink_exception = 0.6
