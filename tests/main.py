# Module:   main
# date:     16th August 2014
# Author:   James Mills, prologic at shortcircuit dot net dot au


"""Main Entrypoint"""


import sys
from types import ModuleType
from os.path import abspath, dirname
from subprocess import Popen, STDOUT


def importable(module):
    try:
        m = __import__(module, globals(), locals())
        return type(m) is ModuleType
    except ImportError:
        return False


def main():
    cmd = ["py.test", "-r", "fsxX", "--ignore=tmp"]

    if importable("pytest_cov"):
        cmd.append("--cov=charla")
        cmd.append("--cov-report=html")

    cmd.append(dirname(abspath(__file__)))

    raise SystemExit(Popen(cmd, stdout=sys.stdout, stderr=STDOUT).wait())

if __name__ == "__main__":
    main()
