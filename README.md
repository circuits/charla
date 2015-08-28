charla
======

charla is [Spanish for chat](http://www.spanishcentral.com/translate/charla) and is an IRC Server and Daemon written in [Python](http://python.org/) using the [circuits](http://circuitsframework.com/) Application Framework.

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

From PyPi (*coming soon*):

    $ pip install charla
    $ charla

Demo
----

There is a demo of the development version of charla running at `daisy.shortcircuit.net.au` on port `7000` if you're interested in testing charla out or want to help out with testing or get involved in the development!

To connect with your favorite IRC Client:

    /server daisy.shortcircuit.net.au 7000

> **note**
>
> The server may often get restarted as it's being developed so please be aware of this!
