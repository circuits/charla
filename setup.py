#!/usr/bin/env python


from glob import glob
from imp import new_module
from os import getcwd, path


from setuptools import setup, find_packages


version = new_module("version")

exec(
    compile(
        open(
            path.join(
                path.dirname(
                    globals().get("__file__", path.join(getcwd(), "charla"))
                ),
                "charla/version.py"
            ),
            "r"
        ).read(),
        "charla/version.py",
        "exec"
    ),
    version.__dict__
)


setup(
    name="charla",
    version=version.version,
    description="Charla IRC Server / Daemon",
    long_description="{0:s}\n\n{1:s}".format(
        open("README.rst").read(), open("CHANGES.rst").read()
    ),
    author="James Mills",
    author_email="James Mills, prologic at shortcircuit dot net dot au",
    url="http://bitbucket.org/prologic/charla/",
    download_url="http://bitbucket.org/prologic/charla/downloads/",
    classifiers=[
        "Development Status :: 1 - Alpha",
        "Environment :: No Input/Output (Daemon)",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Communications :: Chat :: Internet Relay Chat",
    ],
    license="MIT",
    keywords="charla irc server daemon ircd",
    platforms="POSIX",
    packages=find_packages("."),
    include_package_data=True,
    scripts=glob("bin/*"),
    # install_requires=(
    #     "circuits",
    # ),
    entry_points={
        "console_scripts": [
            "charla=charla.main:main",
        ]
    },
    test_suite="tests.main.main",
    zip_safe=False
)
