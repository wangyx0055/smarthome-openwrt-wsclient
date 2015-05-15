#!/bin/sh

#Process param
relogin=${1}
sn=ganzhi123
mac=`ifconfig eth0 | grep HWaddr | awk '{print $5}'`

#Log File
logfile=/tmp/ws_client_launch.log

logsize_limits(){
    logsize=`du -k ${logfile}| awk '{print $1}'`
    if [ ${logsize} -ge 1024 ];then
    	rm -rf ${logfile}
    fi
    return 0
}

# Delete the logfile if the size of logfile exceed 512K
logsize_limits

# Probe the connection ability to the websocket server
url=`/sbin/uci get ezwrt.clsconfig.perceptionurl`
if [ -n ${url} ]; then
    echo "`date`: perception url is null,now execute lbps routine" >> ${logfile}
    lbps=`cd /usr/lib/lua/dm;/usr/bin/lua /usr/lib/lua/dm/perception_lbps.lua` 
    echo ${lbps} >> ${logfile}
fi

# If the websocket client is exist in local host
process=`ps | grep ws_server.py`
result=`echo ${process} | grep -e "python /usr/sbin/ws_server.py*"`

# Launch local websocket client
echo "`date`: sn = ${sn},mac = ${mac},relogin = ${relogin}" >> ${logfile}
if [ -z "${result}" ] && [ -n "${sn}" ] && [ -n "${mac}" ]; then
    echo "`date`: Begin to launch websocket client ......" >> ${logfile}
    $python ws_server.py ${sn} ${mac} ${url}
    echo "`date`: Success to launch websocket client ......" >> ${logfile}
fi

exit 0
