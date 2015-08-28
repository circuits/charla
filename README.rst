.. _Python: http://python.org/
.. _circuits: http://circuitsframework.com/
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

Demo
----

There is a demo of the development version of charla running at ``daisy.shortcircuit.net.au`` on port ``7000``
if you're interested in testing charla out or want to help out with testing or get involved in the development!

To connect with your favourite IRC Client::
    
    /server daisy.shortcircuit.net.au 7000

.. note:: The server may often get restarted as it's being developed so please be aware of this!
