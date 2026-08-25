CircuitPython Base-Application
==============================

Many of my applications use the same logic over and over again. This
repository provides a framework that extracts the basic logic into a
library.

Typical applications include this repo as a submodule and link the
directory `base_app` into their source-tree.


Features
--------

The framework provides the following features:

  - An `UIApplication` with a standard MVC application design (controller).
    The application implements a *data-provider* (model) for the data and
    an *ui-provider* for the view.
  - An abstraction layer supporting different development boards. These
    typically provide buttons and other peripherals in a non-uniform way
    making hardware-agnostic programming complicated. Note that standard
    CircuitPython abstractions like `board.DISPLAY` don't need an additional
    abstraction layer.
  - A configuration layer for *application specific hardware*, e.g. for
    displays that are not part of the development board and therefore lack
    a simple `board.DISPLAY` to access them.
  - A configuration system for network credentials.
  - A configuration system for application specific configurations.


Installation
------------

Add this repository as a submodule and link to the relevant library files
using symbolic links:

    git submodule add https://github.com/bablokb/circuitpython-base-app/ external/base-app
    mkdir src
    cd src
    ln -s ../external/base-app/base_app .

With this setup, you can import e.g. `UIApplication` with

    from base_app.ui_application import UIApplication


Template Application
--------------------

The directory `template` contains a complete template application that
provides blueprints for a main application file `main.py` as well as
basic implementations of a data-provider (`simple_dataprovider.py`) and
ui-provider (`simple_uiprovider.py`). Templates for `settings.py` and
`ui_settings.py` are also provided.


Configuration
-------------

For the configuration of your application, you need to provide a file
`settings.py` that creates a number of value-holder objects:

  - `secrets`: network credentials
  - `app_config`: application configuration
  - `hw_config`: hardware-configuration

Use the blueprint `settings.py` and adopt it to your needs.
See the [Configuration Refererence](./config-reference.md) for details.


Hardware Abstraction Layer and hw_config
----------------------------------------

CircuitPython offers basic hardware abstraction within the
`board`-module.  Boards with an integrated display provide
e.g. `board.DISPLAY`. This abstraction is fine as long as you only use
the display. Some boards also have integrated buttons or other
peripherals. The MagTag for example defines `board.BUTTON_A`, while
the Badger2040W defines `board.SW_A`.

Therefore boards with peripherals beyond a display usually need a
suitable hardware abstraction layer class. For details, read the
[HAL Guide](./hal-guide.md).

Simple dev-boards without peripherals don't need a dedicated
HAL-class. There is a base class that takes care of most of the
requirements. Nevertheless, you have to tell the application which
peripherals to use, e.g. how to create the display-object for an
externally attached display.

This is where the `hw_config` object mentioned above steps in. It allows
the definition of attributes and methods that are mixed into the base
HAL class on the fly:

    def _create_display(hal):
      """ create display for a Sharp Memory Display """

      displayio.release_displays()
      spi = busio.SPI(SCK_PIN,MOSI=MOSI_PIN)
      atexit.register(at_exit,spi)

      framebuffer = sharpdisplay.SharpMemoryFramebuffer(spi,CS_PIN,WIDTH,HEIGHT)
      return framebufferio.FramebufferDisplay(framebuffer, auto_refresh=False)

    class Settings:
      pass

    hw_config     = Settings()
    hw_config.get_display = _create_display
    hw_config.gamut = "mono"
    hw_config.eink  = False

This code-snippet defines a factory method for the display
(`_create_display()`) and assignes it to
`hw_config.get_display`. `get_display()` is a method of the base HAL
class, and during initialization `hw_config` is merged and will
replace this method on the fly.
