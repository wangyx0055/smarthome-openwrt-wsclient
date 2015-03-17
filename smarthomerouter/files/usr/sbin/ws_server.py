#!/usr/bin/env python

from __future__ import print_function
import websocket
import pycurl
import urllib
import StringIO
import sys
import json
import logging
import time
import threading
from apitools import api_call 


if __name__ == "__main__":
    websocket.enableTrace(True)
    logger = logging.getLogger()

    sn = sys.argv[1]
    mac = sys.argv[2]

    logger.debug("sn is %s" % sn)
    logger.debug("mac is %s" % mac)
  
    logger.debug("ws create connection")
    ws = websocket.create_connection("ws://182.92.232.157:8080")
    #ws = websocket.create_connection("wss://ws-dev.ezlink-wifi.com:8888")
    #ws = websocket.create_connection("ws://60.206.36.142:8888/")
    #ws = websocket.create_connection("ws://60.206.137.246:3000/")

    if not ws:
        logger.debug("socket create failed")
    #received = ws.recv()
    
    ws_access_obj_req = {"type":"auth","sn":sn,"mac":mac}
    ws.send(json.dumps(ws_access_obj_req))

    received = ws.recv()
    logger.debug("ws received: '%s'" % received)
    ws_access_obj_rsp = json.loads(received)

    token = ws_access_obj_rsp['token']
    if not token:
        logger.debug("token is null")
        exit()
    logger.debug("token is %s" % token)

    ws_access_obj_req = {"type":"connect","token":token,"sn":sn,"c_type":"router"}
    ws.send(json.dumps(ws_access_obj_req))

    received = ws.recv()
    logger.debug("ws received: '%s'" % received)
    ws_access_obj_rsp = json.loads(received)

    message = ws_access_obj_rsp['message']
    if message != 'connected':
        logger.debug("not connected")
        exit()
    else:
	logger.debug("lizm connect response : '%s'" % message)
	
    def send_notification():
    	wsid = 1
    	while True:
    	    time.sleep(5)
    	    
    	    logger.debug("send_notification begin execute ")
    	    logger.debug("wsid = %d",wsid)
    	    
            api_json_rsp = api_call("net","get_network_associate_list","")
            api_obj_rsp = json.loads(api_json_rsp)
            ws_obj_rsp = {"type":"api_notification"}
            ws_obj_rsp["data"] = api_obj_rsp['result']
            ws_obj_rsp["wsid"] = '%d'%wsid
            #ws_obj_rsp["wsid"] = "1234567890"
            #ws_obj_rsp["from"] = ws_obj_req['from']
            ws_obj_rsp["from"] = sn 
            ws_json_rsp = json.dumps(ws_obj_rsp)
            logger.debug("ws notification send: %s" % ws_json_rsp)
            ws.send(ws_json_rsp)
            wsid+=1
    	    logger.debug("wsid = +1  %d",wsid)
            
    	    logger.debug("send_notification end execute, and next loop after 5s ")
    	
    thread = threading.Thread(target=send_notification)
    thread.daemon = True
    thread.start()

    while True:
        logger.debug("lizm waiting for websocket ...")
        try:
            received = ws.recv()
        except:
            logger.debug("socket except !!!!!!")
            break 

        logger.debug("ws received: '%s'" % received)
        try:
            ws_obj_req = json.loads(received)
        except Exception ,e:
            logger.debug("json err")
            break

        if ws_obj_req.has_key("type") and ws_obj_req['type'] == 'api_rest':
            data = ws_obj_req['data']
            api_json_rsp = api_call(data['apiclass'],data['method'],data['params'])
            api_obj_rsp = json.loads(api_json_rsp)
            ws_obj_rsp = {"type":"api_router"}
            ws_obj_rsp["data"] = api_obj_rsp['result']
            ws_obj_rsp["wsid"] = ws_obj_req['wsid']
            ws_obj_rsp["from"] = ws_obj_req['from']
            ws_json_rsp = json.dumps(ws_obj_rsp)
            logger.debug("ws send: %s" % ws_json_rsp)
            ws.send(ws_json_rsp)

        else:
            logger.debug("unrecognize message")
            
    ws.close()

