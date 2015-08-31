# Module:   events
# Date:     16th August 2014
# Author:   James Mills, prologic at shortcircuit dot net dot au


"""Events Module

This module defines events shared by various componetns.
"""


from circuits import Event


class cmd(Event):
    """cmd Event"""


class broadcast(Event):
    """broadcast Event"""


class terminate(Event):
    """terminate Event"""


class signon(Event):
    """signon Event"""


class rehashed(Event):
    """rehashed Event"""
