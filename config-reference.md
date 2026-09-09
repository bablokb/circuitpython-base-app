Configuration Reference
=======================

Overview
--------

Configuration needs a file named `settings.py` with three objects:

    class Settings:
      pass

    secrets = Settings()
    hw_config = Settings()
    app_config = Settings()

The first object contains network credentials, the second object hardware
definitions and the third object application specific configuration.


Network Credentials
-------------------

The `secrets`-object contains settings that are needed to connect to a WLAN.
Only `ssid` and `password` are necessary, all other settings are optional:

    secrets.ssid      = 'my-ssid'
    secrets.password  = 'my-secret-password'
    #secrets.retry     = 2
    #secrets.debugflag = False
    #secrets.channel   = 6
    #secrets.timeout   = 10


Hardware Configuration
----------------------

With `hw_config`, you can add and override attributes and methods of
the base HAL class (class `HalBase` in
[`base_app/hal/hal_base.py`](base_app/hal/hal_base.py)). Usually, only
a few attributes and methods need to be provided.

Currently supported attributes and methods:

  - `BUTTONS = None`: A tuple: `([pin, ...], value, pull)`. The first
     element is a list of pins (GPIOs). The second element is the value
     of the pins when pressed, the last element configures automatic
     pulls for the pins.
  - `WAKE_PINS = None`: A tuple: `([pin, ...], value, edge,
    pull)`. Pin list, value and pull as above. Use `edge=True` if the
    pin triggers on edge-changes, otherwise (i.e. level-triggered) use
    `edge=False`.
  - `RTC = "NoRTC"`. One of the supported external RTCs:
       - "PCF8523"
       - "PCF8563"
       - "PCF85063"
       - "OsRTC"
     For details, see the files in `base_app/ext_rtc`.
  - Standard attributes from the `board`-module (e.g. `SDA`, `SCL` etc.) can
    be overridden from `hw_config`. One use case for example: the application
    LED must not necessarily be the board-LED.
  - `init(hal)`: one-time initialization, e.g. to mount a SD
  - `led(value,color=[255,0,0])`: A method to override led blink behavior.
  - `bat_level()`: A method to return the battery level.
  - `get_wifi(debug=False)`: Factory method for the wifi-interface. Needed
    for non-native wifi-implementations (e.g. using a Wiznet-chip or an
    ESP32AT-coprocessor).
  - `get_display(hal)`: Factory method to create a display-object.
  - `get_rtc_ext(net_update=False, debug=False)`: Factory method for
    non-standard RTCs.
  - `update_rtc(ts)`: Update RTC (internal and external). Needed only
    for non-standard RTCs.
  - `shutdown()`: Implement shutdown (power off). The default is a no-op.
  - `shutdown_emulate`: If `True`, exit the program.
  - `shutdown_delay`: Number of seconds to wait before exit.
  - `at_exit()`: At-exit processing to free ressources.
  - `sleep(duration)`: Sleep implementation.
  - `get_keypad(hal)`: Factory method for creating a `Keypad` object. The
    default uses the GPIOs defined with `BUTTONS`.
  - `check_key(name)`: Test if a given key has been pressed.
  - `get_pin_alarms(hal)`: Return a list of pin-alarms defined for this board.
  - `deep_sleep(alarms=[], wakeup=None)`: Implement deep-sleep.
  - `nvram_read(offset, count)`: Read bytes from NVRAM.
  - `nvram_write(offset, data)`: Write bytes to NVRAM.
