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

  - A `UIApplication` with a standard MVC application design (controller).
    The application implements a *data-provider* (model) for the data and
    an *ui-provider* for the view.
  - An abstraction layer supporting different development boards. These
    typically provide buttons and other peripherals in a non-uniform way
    making hardware-agnostic programming complicated. Note that standard
    CircuitPython abstractions like `board.DISPLAY` don't need and additional
    abstraction layer.
  - A configuration layer for application specific hardware, e.g. for
    displays that are not part of the development board and therefore lack
    a simple `board.DISPLAY` to access them.
  - A configuration system for network credentials.
  - A configuration system for application specific configurations.


Installation
------------

Add this repository as a submodule and link to the relevant library files
using symbolic links:

    git add submode https://github.com/bablokb/circuitpython-base-app/ external/base-app
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
`settings.py` that provides a number of value-holder objects:

  - `secrets`: network credentials
  - `app_config`: application configuration
  - `hw_config`: hardware-configuration

Use the blueprint `settings.py` and adopt it to your needs.
