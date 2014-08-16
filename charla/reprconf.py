# Module:   reprconf
# Date:     16th August 2014
# Author:   James Mills, prologic at shortcircuit dot net dot au
#
# NOTE:     Borrowed from CherryPy3
#
# Borrowed from sahriswiki (https://sahriswiki.org/)
# with permission from James Mills, prologic at shortcircuit dot net dot au


"""Generic configuration system using unrepr.

Configuration data may be supplied as a Python dictionary, as a filename,
or as an open file object. When you supply a filename or file, Python's
builtin ConfigParser is used (with some extensions).
"""


from ConfigParser import ConfigParser


from .unrepr import unrepr


def as_dict(config):
    """Return a dict from 'config' whether it is a dict, file, or filename."""
    if isinstance(config, str):
        config = Parser().dict_from_file(config)
    elif hasattr(config, 'read'):
        config = Parser().dict_from_file(config)
    return config


class Config(dict):
    """A dict-like set of configuration data.

    May take a file, filename, or dict.
    """

    defaults = {}
    environments = {}

    def __init__(self, file=None, **kwargs):
        super(Config, self).__init__()

        self.reset()
        if file is not None:
            self.update(file)
        if kwargs:
            self.update(kwargs)

    def reset(self):
        """Reset self to default values."""
        self.clear()
        dict.update(self, self.defaults)

    def update(self, config):
        """Update self from a dict, file or filename."""
        if isinstance(config, str):
            # Filename
            config = Parser().dict_from_file(config)
        elif hasattr(config, 'read'):
            # Open file object
            config = Parser().dict_from_file(config)
        else:
            config = config.copy()
        self._apply(config)

    def _apply(self, config):
        """Update self from a dict."""
        which_env = config.get('environment')
        if which_env:
            env = self.environments[which_env]
            for k in env:
                if k not in config:
                    config[k] = env[k]

        dict.update(self, config)

    def __setitem__(self, k, v):
        dict.__setitem__(self, k, v)


class Parser(ConfigParser):
    """Sub-class of ConfigParser that keeps the case of options and that raises
    an exception if the file cannot be read.
    """

    def optionxform(self, optionstr):
        return optionstr

    def read(self, filenames):
        if isinstance(filenames, str):
            filenames = [filenames]
        for filename in filenames:
            # try:
            #     fp = open(filename)
            # except IOError:
            #     continue
            fp = open(filename)
            try:
                self._read(fp, filename)
            finally:
                fp.close()

    def as_dict(self, raw=False, vars=None):
        """Convert an INI file to a dictionary"""
        # Load INI file into a dict
        result = {}
        for section in self.sections():
            if section not in result:
                result[section] = {}
            for option in self.options(section):
                value = self.get(section, option, raw, vars)
                try:
                    value = unrepr(value)
                except Exception as x:
                    msg = ("Config error in section: %r, option: %r, "
                           "value: %r. Config values must be valid Python." %
                           (section, option, value))
                    raise ValueError(msg, x.__class__.__name__, x.args)
                result[section][option] = value
        return result

    def dict_from_file(self, file):
        if hasattr(file, 'read'):
            self.readfp(file)
        else:
            self.read(file)
        return self.as_dict()
