#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import websocket
import pycurl
import urllib
import StringIO
import sys
import json
import logging
import logging.handlers
LOG_FILENAME='/tmp/websocket.log'
import time
import threading
from apitools import api_call 

g_user_list = []

if __name__ == "__main__":
    websocket.enableTrace(True)
    logger = logging.getLogger()
    handler = logging.handlers.RotatingFileHandler(LOG_FILENAME,
            maxBytes=1048576,
            backupCount=3,
            )
    logger.addHandler(handler)
    
    def send_notification(msg):
    	ws.send(msg)
    	
    def encode_router_status_notification(sn,msg):
    	ws_obj_rsp = {"type":"notification"}                                                  
    	ws_obj_rsp["wsid"] = 888                                                                  
    	ws_obj_rsp["from"] = sn
    	
    	data = {"msgtype":"reboot"}
    	data["message"] = msg
    	ws_obj_rsp["data"] = data
    	ws_json_rsp = json.dumps(ws_obj_rsp)
        send_notification(ws_json_rsp)

    sn = sys.argv[1]
    mac = sys.argv[2]

    logger.debug("sn is %s" % sn)
    logger.debug("mac is %s" % mac)
  
    logger.debug("ws create connection")
    ws = websocket.create_connection("ws://123.57.12.142:8080")
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
	encode_router_status_notification(sn,'路由器上线成功')
	
    def encode_device_state_notification(sn,islogin,msg):
    	ws_obj_rsp = {"type":"notification"}
    	ws_obj_rsp["wsid"] = 888
    	ws_obj_rsp["from"] = sn 
    	
    	data = {"msgtype":"subdevstate"}
    	
    	data["islogin"] = islogin
    	data["mac"] = msg["macaddr"]
    	ws_obj_rsp["data"] = data
    	ws_json_rsp = json.dumps(ws_obj_rsp)
    	send_notification(ws_json_rsp)
    	
    	logger.debug("send notification = %s",ws_json_rsp)
    	
    def send_notification_thread():
    	wsid = 1
    	while True:
    	    time.sleep(3)
    	    
#    	    logger.debug("send_notification_thread begin execute ")
    	    
            api_json_rsp = api_call("net","get_network_associate_list","")
            api_obj_rsp = json.loads(api_json_rsp)
            
            results = api_obj_rsp["result"]
            #logger.debug("lizm: len(results) %d" , len(results))
            
            for result in results:
            	#logger.debug("result: mac = %s",result["macaddr"])
            	found = 0
            	for i, x in enumerate(g_user_list):
            		if x["macaddr"] == result["macaddr"]:
            			found = 1
            			break
            	if found == 0:
            		g_user_list.append(result)		
            		logger.debug("Should notification mac  %s logger on",result["macaddr"])
            		encode_device_state_notification(sn,"1",result)
 			
            for j,y in enumerate(g_user_list):
            	found = 0 
            	for result in results:
            		if y["macaddr"] == result["macaddr"]:
            			found = 1
            			break
            	if found == 0:
            		logger.debug("Should notification mac  %s logger off",y["macaddr"])
            		g_user_list.remove(y)
            		encode_device_state_notification(sn,"0",y)
            	
#    	    logger.debug("send_notification end execute, and next loop after 3s ")
    	
    thread = threading.Thread(target=send_notification_thread)
    thread.daemon = True
    thread.start()

    while True:
        logger.debug("waiting for websocket ...")
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

        if ws_obj_req.has_key("type") and ws_obj_req['type'] == 'rest':
            data = ws_obj_req['data']
            if data['method']=='reboot':
    		encode_router_status_notification(sn,'路由器正在重启...')
    		
            api_json_rsp = api_call(data['apiclass'],data['method'],data['params'])
            api_obj_rsp = json.loads(api_json_rsp)
            ws_obj_rsp = {"type":"router"}
            ws_obj_rsp["data"] = api_obj_rsp['result']
            ws_obj_rsp["wsid"] = ws_obj_req['wsid']
            ws_obj_rsp["from"] = ws_obj_req['from']
            ws_json_rsp = json.dumps(ws_obj_rsp)
            logger.debug("ws send: %s" % ws_json_rsp)
            ws.send(ws_json_rsp)

        else:
            logger.debug("unrecognize message")
            
    ws.close()

