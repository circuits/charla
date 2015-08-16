.. _Python: http://python.org/
.. _circuits: http://circuitsframework.org/
.. _Docker: https://www.docker.com/
.. _Docker Compose: https://github.com/docker/compose


charla
======

charla is `Spanish for chat <http://www.spanishcentral.com/translate/charla>`_
and is an IRC Server and Daemon written in `Python`_ using the `circuits`_
Application Framework.


Installation and Usage
----------------------

From Source::
    
    $ git clone https://github.com/prologic/charla.git
    $ cd charla
    $ pip install -r requirements.txt
    $ python setup.py develop
    $ charla

From Source using `Docker Compose`_ and `Docker`_::
    
    $ git clone https://github.com/prologic/charla.git
    $ cd charla
    $ docker-compose up

Using `Docker`_::
    
    $ docker run -d 7000:7000 prologic/charla

From PyPi (*ccoming soon*)::
    
    $ pip install charla
    $ charla
