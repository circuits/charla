#!/usr/bin/env python


from glob import glob


from setuptools import setup, find_packages


def parse_requirements(filename):
    with open(filename, "r") as f:
        for line in f:
            if line and line[:2] not in ("#", "-e"):
                yield line.strip()


setup(
    name="charla",
    description="Charla IRC Server / Daemon",
    long_description=open("README.rst", "r").read(),
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
    install_requires=list(parse_requirements("requirements.txt")),
    entry_points={
        "console_scripts": [
            "charla=charla.main:main",
        ]
    },
    test_suite="tests.main.main",
    zip_safe=False,
    use_scm_version={
        "write_to": "charla/version.py",
    },
    setup_requires=[
        "setuptools_scm"
    ],
)
