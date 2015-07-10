FROM python:2.7-onbuild

EXPOSE 6667/tcp

ENTRYPOINT ["charla"]

RUN python setup.py install
