# Docker Image for charla IRC Daemon

FROM prologic/crux-python
MAINTAINER James Mills, prologic at shortcircuit dot net dot au

# Services
EXPOSE 6667

# Startup
ENTRYPOINT ["/usr/bin/charla"]

# Runtime Dependencies
ADD requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt && rm /tmp/requirements.txt

# Application
WORKDIR /app
ADD . /app
RUN python setup.py install
