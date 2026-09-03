# ----------------------------------------------------------------------------
# __init__.py: Hardware-Abstraction-Layer module.
#
# This module implements the get_hal() helper method.
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/circuitpython-base-app
# ----------------------------------------------------------------------------

import builtins
import board

# --- get HAL   ------------------------------------------------------------

# Import HAL (hardware-abstraction-layer).
# This expects an object "impl" within the implementing hal_file.
# All hal implementations are within base_app/hal/. Filenames must be
# sanitized board.board_id.py, e.g. src/hal/pimoroni_inky_frame_5_7.py

def get_hal(msg_printer=None):
  """ read and return hal-object """

  try:
    hal_file = "base_app.hal."+board.board_id.replace(".","_")
    hal_module = builtins.__import__(hal_file,None,None,["impl"],0)
    if msg_printer:
      msg_printer("using board-specific implementation")
  except Exception as ex:
    if msg_printer:
      msg_printer(f"info: no board specific HAL (ex: {ex})")
    if hal_file.startswith("RASPBERRY_PI"):
      # use GENERIC_LINUX_PC
      hal_file = "base_app.hal.GENERIC_LINUX_PC"
      if msg_printer:
        msg_printer("info: using default implementation from HalBase")
    else:
      hal_file = "base_app.hal.hal_default"
      if msg_printer:
        msg_printer("info: using default implementation from HalBase")

  hal_module = builtins.__import__(hal_file,None,None,["impl"],0)
  return hal_module.impl
