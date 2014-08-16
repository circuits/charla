# Module:   data
# Date:     16th August 2014
# Author:   James Mills, prologic at shortcircuit dot net dot au


"""Data Handling"""


from attrdict import AttrDict


class Data(AttrDict):
    """An attribute access data dictionary

    An `attrdict <https://pypi.python.org/pypi/attrdict>`_
    attribute access style dictionary with a way to
    "initialize" the dictionary with another non-overriding
    dict preserving any already existing keys.
    """

    def init(self, D):
        """Data.init(D)

        Initializes ``Data`` with keys and values
        from ``D`` only if they do not already exist
        in ``Data``. Similar to ``dict.update`` but
        with non-overriding behavior. Useful for
        populating a dict with some initial data.

        :param dict D: non-overriding data to populate with
        :return: the updated dictionary
        :rtype: dict
        """

        for k, v in D.items():
            if k not in self:
                self[k] = v
