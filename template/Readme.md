Template Application Files
==========================

Overview
--------

This folder contains a number of template application files. You can use
these files as a blueprint for real applications.


main.py
-------

This is the top-level file (you can also name it `code.py`). This file
will typically instantiate the data-provider and ui-provider, and subclass
`base_app.ui_application`. Then it will run either `app.run_once()` or
`app.run()`. Use the former for application designs where the mcu shuts down
after running the application code.


Data-Provider
-------------

The file `simple_dataprovider.py` implements the class `DataProvider`. This
class must implement a number of methods, mainly `update_data()`. The method
is called with a dict as argument and the method is expected to add/update
the dict.


UI-Provider
-----------

The file `simple_uiprovider.py` implements the class `UIProvider`. This
class must implement a number of methods, mainly `create_ui()` and
`update_ui()`. The former is called once. It should create the view
(typically a `displayio.Group`), the latter called during every iteration
of `app.run()`. The method is called with the data-dict.


settings.py
-----------

This is the application configuration file. It must create a number of
value-holder objects:

  - `secrets`: network credentials
  - `hw_config`: application-specific hardware configuration
  - `app_config`: application-specific configuration

Use the template file as a blueprint and adapt it to your needs. For the
template-application, the `app_config` object only implements a single
configuration variable `app_config.full` that is used by the ui-provider
to format the data. For real-world applications you can have any number
of configuration variables.

For `secrets` and `hw_config`, the naming of the config-variables is fixed,
but you only need to provide variables that you actually use. E.g. you
only have to set `hw_config.get_keypad` if you actually use keys within
your application.

Note that some of the values of config-variables are simple values, while
others are references to methods. E.g.

    hw_config.get_keypad  = _get_keypad      # correct
    hw_config.get_keypad  = _get_keypad()    # wrong!

The first (correct) line sets `hw_config.get_keypad` to a method-definition,
where as the second line would set `hw_config.get_keypad` to the result
of the method-call, which is wrong because the method gets called later
from the framework.


ui_settings.py
--------------

This is an optional file with (reusable) settings used by the
ui-provider. Depending on how you implement the ui-provider, you might
or might not want to use a dedicated ui-settings file.
