#!/usr/bin/env python

from __future__ import print_function
import websocket
import urllib
import StringIO
import json

if __name__ == "__main__":
    websocket.enableTrace(True)
    #ws = websocket.create_connection("ws://182.92.232.157:8080/")
    ws = websocket.create_connection("ws://192.168.56.103:1234/")

    while True:
        data = raw_input("data: ")
        ws.send(data)
        received = ws.recv()
        print("Received '%s'" % received)

    ws.close()
