#!/usr/bin/env python

from __future__ import print_function
from apitools import api_call
import sys

if __name__ == "__main__":
    index = 0
    method = ""
    params = []
    pi = 0
    for arg in sys.argv:
        if index == 1:
            apiclass = arg
        if index == 2:
            method = arg
        if index > 2:
            params[pi] = arg
            pi += 1
        index += 1 
    ret = api_call(apiclass,method,params)
    print("%s" % ret)
