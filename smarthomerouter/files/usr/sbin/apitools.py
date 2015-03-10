#!/usr/bin/env python

from __future__ import print_function
import pycurl
import urllib
import StringIO
import json

def api_call(apiclass,method,params):
    apiclass = str(apiclass)
    print("apiclass:%s" % apiclass)

    method = str(method)
    print("method:%s" % method)

    plist = "["
    index = 0
    for val in params:
        plist += "\"" + str(val) + "\""
        if index < (len(params)-1):
            plist += ","
        index += 1
    plist += "]"
    print("params:%s" % plist)

    url = "http://127.0.0.1/cgi-bin/luci/api/"+apiclass+"?auth=myluckday"
    data = "{\"method\":\"" + method + "\",\"params\":" + plist + "}"
    print("url:%s" % url)
    print("post:%s" % data)

    crl = pycurl.Curl()
    crl.setopt(crl.FAILONERROR,True)

    crl.setopt(pycurl.URL,url)
    crl.setopt(crl.POSTFIELDS,data)

    crl.fp = StringIO.StringIO()
    crl.setopt(crl.WRITEFUNCTION,crl.fp.write)

    try:
        crl.perform()
    except pycurl.error,error:
        errno,errstr = error
        print("curl error:%s" % errstr)

    return crl.fp.getvalue()

