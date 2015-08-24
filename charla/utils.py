"""Utilities Module"""


from time import sleep
from socket import AF_INET, SOCK_STREAM, socket


def waitfor(address, port, timeout=10):
    sock = socket(AF_INET, SOCK_STREAM)
    counter = timeout
    while not sock.connect_ex((address, port)) == 0 and counter:
        sleep(1)
        counter -= 1
