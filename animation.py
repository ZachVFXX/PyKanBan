import time

import pywinstyles


def fade_out(
    widget_parent, widget_id: int, from_: int = 100, to: int = 0, step: int = -10
):
    """
    Fade a widget out from x% to y% over a specified time period.

    :param widget_parent: in general self.
    :argument widget_id: The widget to fade.
    :argument from_: The starting opacity value (0-100).
    :argument to: The ending opacity value (0-100).
    :argument step: The step size to fade by.
    """
    if type(widget_id) is not int:
        raise TypeError("You must provide the widget_id as an integer")
    if type(from_) is not int:
        raise TypeError("You must provide the from_ as an integer")
    if type(to) is not int:
        raise TypeError("You must provide the to as an integer")
    if type(step) is not int:
        raise TypeError("You must provide the step as an integer")

    for i in range(from_, to, step):
        if not widget_parent.winfo_exists():
            break
        pywinstyles.set_opacity(widget_id, value=i / 100)
        widget_parent.update()
        time.sleep(1 / 100)


def fade_in(widget_parent, widget_id: int, from_=0, to=100, step: int = 10):
    """
    Fade a widget in from x% to y% over a specified time period.

    :argument widget_parent: in general self.
    :argument widget_id: The widget to fade.
    :argument from_: The starting opacity value (0-100).
    :argument to: The ending opacity value (0-100).
    :argument step: The step size to fade by.
    """
    if type(widget_id) is not int:
        raise TypeError("You must provide the widget_id as an integer")
    if type(from_) is not int:
        raise TypeError("You must provide the from_ as an integer")
    if type(to) is not int:
        raise TypeError("You must provide the to as an integer")
    if type(step) is not int:
        raise TypeError("You must provide the step as an integer")
    for i in range(from_, to, step):
        if not widget_parent.winfo_exists():
            break
        pywinstyles.set_opacity(widget_id, value=i / 100)
        widget_parent.update()
        time.sleep(1 / 100)
