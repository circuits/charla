# Package:  version
# Date:     16th August 2014
# Author:   James Mills, prologic at shortcircuit dot net dot au


"""Version Module

So we only have to maintain version information in one place!
"""


version_info = (0, 0, 1, "dev")  # (major, minor, patch, dev?)
version = ".".join(map(str, version_info))
