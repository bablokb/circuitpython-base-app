# -------------------------------------------------------------------------
# This file contains settings related to the UI.
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/circuitpython-base-app
# -------------------------------------------------------------------------

from displayio import Palette

class Settings:
  pass

UI_PALETTE    = Palette(7)
UI_PALETTE[0] = 0xFFFFFF
UI_PALETTE[1] = 0x000000
UI_PALETTE[2] = 0x0000FF
UI_PALETTE[3] = 0x00FF00
UI_PALETTE[4] = 0xFF0000
UI_PALETTE[5] = 0xFFFF00
UI_PALETTE[6] = 0xFFA500

COLOR = Settings()
COLOR.WHITE  = 0
COLOR.BLACK  = 1
COLOR.BLUE   = 2
COLOR.GREEN  = 3
COLOR.RED    = 4
COLOR.YELLOW = 5
COLOR.ORANGE = 6

# map color-names to (FG_INDEX,BG_INDEX)
UI_COLOR_MAP = {
  "white":  (COLOR.WHITE,COLOR.BLACK),
  "black":  (COLOR.BLACK,COLOR.WHITE),
  "blue":   (COLOR.BLUE,COLOR.WHITE),
  "green":  (COLOR.GREEN,COLOR.WHITE),
  "red":    (COLOR.RED,COLOR.BLACK),
  "yellow": (COLOR.YELLOW,COLOR.BLACK),
  "orange": (COLOR.ORANGE,COLOR.BLACK)
  }

UI_SETTINGS          = Settings()
UI_SETTINGS.MARGIN   = 5
UI_SETTINGS.PADDING  = 3
UI_SETTINGS.FG_INDEX = COLOR.BLACK
UI_SETTINGS.BG_INDEX = COLOR.WHITE
UI_SETTINGS.FG_COLOR = UI_PALETTE[UI_SETTINGS.FG_INDEX]
UI_SETTINGS.BG_COLOR = UI_PALETTE[UI_SETTINGS.BG_INDEX]
