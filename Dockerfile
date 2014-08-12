# Docker Image for charla IRC Daemon

FROM prologic/crux-python
MAINTAINER James Mills, prologic at shortcircuit dot net dot au

ADD . /app
WORKDIR /app
RUN pip install -r requirements.txt

ENTRYPOINT ["/app/server.py"]
