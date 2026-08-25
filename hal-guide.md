Hardware Abstraction Layer Guide
================================

This document describes the architecture of the hardware abstraction layer.
The target audience are developers who want to create board-specific
HAL-files.


Overview
--------

The HAL is a singleton instance of a HAL-class. The class must be
implemented as a subclass of `HalBase` in the file
`base_app/hal/<board_id>.py`. `<board_id>` is the value of the boards
id, i.e. the `board.board_id` attribute. All periods must be replaced
with underscores. The file must instatiate the singleton in the object
`impl`:

    from .hal_base import HalBase

    class HalFooBoard(HalBase):
      """ Badger2040W specific HAL-class """

    def __init__(self):
      """ constructor """
      super().__init__()
      ....

    impl = HalFooBoard()


Implementation
--------------

HAL files are only necessary for boards that provide peripherals that
are not covered by the normal CircuitPython abstraction (i.e. the
`board`-module).  Typical cases are on-board buttons or special
circuitry to power off the board.

A good blueprint is the Pimoroni Badger2040W. This board has an e-ink
display, five buttons, a RTC and power-off circuitry. The abstraction
of the display is covered by `board.DISPLAY`, but the rest of the
components are not covered.

The implementation in
[`base_app/hal/pimoroni_badger2040w.py`](base_app/hal/pimoroni_badger2040w.py)
is simple, since most of the functions implemented in the base class
`HalBase` are sufficient. It only sets a number of attributes and
overrides the `shutdown()`-method to take advantage of the boards
shutdown circuit.


Adding a HAL-File
-----------------

To add a new HAL-file for a board start the CircuitPython-REPL and
run

    import board
    board.board_id.replace(".","_")

This will give you the name of the HAL-file.

Copy one of the existing files in `base_app/hal/` and adapt to your
needs.  There are no restrictions on the name of the HAL-class, but in
case of exception backtraces it makes sense to name it in relation to
the board name.

Don't forget to create a PR for this file so that other users can
benefit from your work.
