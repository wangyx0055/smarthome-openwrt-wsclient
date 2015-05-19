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
import os 
import string
import urllib
import urllib2
from apitools import api_call 

dest= ''
pnun = 0
tid = 0
pingflag = 0
g_user_list = []

host=''
port=80
path='/'

if __name__ == "__main__":
    websocket.enableTrace(True)
    logger = logging.getLogger()
    handler = logging.handlers.RotatingFileHandler(LOG_FILENAME,
            maxBytes=1048576,
            backupCount=3,
            )
    logger.addHandler(handler)
    
    def send_msg(msg):
    	ws.send(msg)
    	
    def encode_router_status_notification(idcode,msg):
    	ws_obj_rsp = {"type":"notification"}                                                  
    	ws_obj_rsp["wsid"] = 888                                                                  
    	ws_obj_rsp["from"] = idcode
    	
    	data = {"msgtype":"reboot"}
    	data["message"] = msg
    	ws_obj_rsp["data"] = data
    	ws_json_rsp = json.dumps(ws_obj_rsp)
        send_msg(ws_json_rsp)
        
    def encode_router_response(wsid,src,data,error):
    	ws_obj_rsp = {"type":"router"}                                                  
        ws_obj_rsp["wsid"] = wsid
        ws_obj_rsp["from"] = src
        ws_obj_rsp["error"] = error 
        
    	ws_obj_rsp["data"] = data
    	ws_json_rsp = json.dumps(ws_obj_rsp)
        send_msg(ws_json_rsp)
        
    pppoeid = sys.argv[1]
    passwd = sys.argv[2]
    mac = sys.argv[3]
    dest = sys.argv[4]
    idcode = sys.argv[5]
    wanip = sys.argv[6]

    logger.debug("idcode is %s" % idcode)
    logger.debug("mac is %s" % mac)
    logger.debug("dest is %s" % dest)
    logger.debug("pppoeid is %s" % pppoeid)
    logger.debug("passwd is %s" % passwd)
    logger.debug("wanip is %s" % wanip)
  
    logger.debug("ws create connection")
    
    try:
    	ws = websocket.create_connection(dest)
    except:
        logger.debug("socket create failed")
        os.system("cd /usr/lib/lua/dm && /usr/bin/lua /usr/lib/lua/dm/perception_lbps.lua")
        exit()
    
    ws_access_obj_req = {"type":"auth","idcode":idcode,"mac":mac}
    ws.send(json.dumps(ws_access_obj_req))

    received = ws.recv()
    logger.debug("ws received: '%s'" % received)
    ws_access_obj_rsp = json.loads(received)

    token = ws_access_obj_rsp['token']
    if not token:
        logger.debug("token is null")
        exit()
    logger.debug("token is %s" % token)

    ws_access_obj_req = {"type":"connect","token":token,"idcode":idcode,"deviceIp":wanip,"pppoeId":pppoeid,"passwd":passwd,"c_type":"router"}
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
	encode_router_status_notification(idcode,'路由器上线成功')
	
    def encode_device_state_notification(idcode,islogin,msg):
    	ws_obj_rsp = {"type":"notification"}
    	ws_obj_rsp["wsid"] = 888
    	ws_obj_rsp["from"] = idcode 
    	
    	data = {"msgtype":"subdevstate"}
    	
    	data["islogin"] = islogin
    	data["mac"] = msg["macaddr"]
    	ws_obj_rsp["data"] = data
    	ws_json_rsp = json.dumps(ws_obj_rsp)
    	send_msg(ws_json_rsp)
    	
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
            		#logger.debug("Should notification mac  %s logger on",result["macaddr"])
            		encode_device_state_notification(idcode,"1",result)
 			
            for j,y in enumerate(g_user_list):
            	found = 0 
            	for result in results:
            		if y["macaddr"] == result["macaddr"]:
            			found = 1
            			break
            	if found == 0:
            		logger.debug("Should notification mac  %s logger off",y["macaddr"])
            		g_user_list.remove(y)
            		encode_device_state_notification(idcode,"0",y)
            	
#    	    logger.debug("send_notification end execute, and next loop after 3s ")

    thread = threading.Thread(target=send_notification_thread)
    thread.daemon = True
    thread.start()

    def ping_thread():
    	while True:
    	    time.sleep(2)
    	    global pingflag
    	    if pingflag == 1 :
    	    	cmd = 'ping '+dest+' -c '+pnum+' >/tmp/'+tid+'.ping'
	    	os.system(cmd);    	
    	    	pingflag = 0
    	    	
    	
    pingthread = threading.Thread(target=ping_thread)
    pingthread.daemon = True
    pingthread.start()
    
    def get_ping_result(wsid,src,tid):
    	filename = '/tmp/'+tid+'.ping'
    	data = {"transmitted":0}
        if os.path.exists(filename):
        	fileHandle = open (filename)
        	content = fileHandle.readlines()
        	filelen = len(content)
        	#if len(content[filelen-1]) != 1:
        	if content[filelen-1].split()[0] == "round-trip":
        		data["min"] = string.atof(content[filelen-1].split()[3].split('/')[0])
        		data["avg"] = string.atof(content[filelen-1].split()[3].split('/')[1])
        		data["max"] = string.atof(content[filelen-1].split()[3].split('/')[2])
        		if content[filelen-2].split()[2] == "transmitted,":
        			data["transmitted"]=string.atoi(content[filelen-2].split()[0])
        			data["received"]=string.atoi(content[filelen-2].split()[3])
        			data["loss"]=content[filelen-2].split()[6]
        	elif content[filelen-1].split()[2] == "transmitted,":
        		data["transmitted"]=string.atoi(content[filelen-1].split()[0])
        		data["received"]=string.atoi(content[filelen-1].split()[3])
        		data["loss"]=content[filelen-1].split()[6]
    			data["min"] = 0
    			data["avg"] = 0
    			data["max"] = 0
        		
		fileHandle.close()        		
		
		
    		encode_router_response(wsid,src,data,0)
    		cmd = 'rm -rf '+filename
    		os.system(cmd)
    	else:
    		data["received"]=0
    		data["loss"]="0%"
    		data["min"] = 0
    		data["avg"] = 0
    		data["max"] = 0
    		encode_router_response(wsid,src,data,0)
        		
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
    		encode_router_status_notification(idcode,'路由器正在重启...')
    		encode_router_response(ws_obj_req['wsid'],ws_obj_req['from'],{},0)
    		#continue
    	    elif data['method']=='ping':
    		pingparam = data['params']
    		encode_router_response(ws_obj_req['wsid'],ws_obj_req['from'],{},0)
    		if pingflag == 0:
    			dest = pingparam[0]
    			pnum = pingparam[1]
    			tid = pingparam[2]
    			pingflag = 1
    		continue 
    	    elif data['method']=='getPingResult':
    	    	logger.debug("get ping result")
    	    	pingparam = data['params']
    	    	get_ping_result(ws_obj_req['wsid'],ws_obj_req['from'],pingparam[0])
    	    	continue
    	    	
            api_json_rsp = api_call(data['apiclass'],data['method'],data['params'])
            api_obj_rsp = json.loads(api_json_rsp)
            ws_obj_rsp = {"type":"router"}
            ws_obj_rsp["data"] = api_obj_rsp['result']
            ws_obj_rsp["error"] = 0
            ws_obj_rsp["wsid"] = ws_obj_req['wsid']
            ws_obj_rsp["from"] = ws_obj_req['from']
            ws_json_rsp = json.dumps(ws_obj_rsp)
            logger.debug("ws send: %s" % ws_json_rsp)
            ws.send(ws_json_rsp)

        else:
            logger.debug("unrecognize message")
            
    ws.close()

