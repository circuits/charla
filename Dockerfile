FROM python:2.7-onbuild

EXPOSE 7000

ENTRYPOINT ["charla"]

RUN python setup.py install
