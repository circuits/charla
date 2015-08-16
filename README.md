charla
======

charla is [Spanish for chat](http://www.spanishcentral.com/translate/charla) and is an IRC Server and Daemon written in [Python](http://python.org/) using the [circuits](http://circuitsframework.org/) Application Framework.

Installation and Usage
----------------------

From Source:

    $ git clone https://github.com/prologic/charla.git
    $ cd charla
    $ pip install -r requirements.txt
    $ python setup.py develop
    $ charla

From Source using [Docker Compose](https://github.com/docker/compose) and [Docker](https://www.docker.com/):

    $ git clone https://github.com/prologic/charla.git
    $ cd charla
    $ docker-compose up

Using [Docker](https://www.docker.com/):

    $ docker run -d 7000:7000 prologic/charla

From PyPi (*ccoming soon*):

    $ pip install charla
    $ charla
