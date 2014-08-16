# Docker Image for charla IRC Daemon

FROM prologic/crux-python
MAINTAINER James Mills, prologic at shortcircuit dot net dot au

ADD . /app
WORKDIR /app
RUN pip install -r requirements.txt
RUN python setup.py install

ENTRYPOINT ["/usr/bin/charla"]
