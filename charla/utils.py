# Module:   utils
# Date:     16th August 2014
# Author:   James Mills, prologic at shortcircuit dot net dot au


"""Utilities Module"""


def anyof(obj, *types):
    return any(isinstance(obj, type) for type in types)
