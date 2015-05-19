#!/bin/sh

#Process param
relogin=${1}

# get pppoe username
pppoeid=`/sbin/uci get network.wan.username`
if [ -z ${pppoeid} ]; then
    pppoeid=`cd /usr/lib/lua/dm ; lua /usr/lib/lua/dm/get_idcode.lua`
fi

# get pppoe passwd 
password=`/sbin/uci get network.wan.password`
if [ -z ${password} ]; then
    password=`cd /usr/lib/lua/dm ; lua /usr/lib/lua/dm/get_idcode.lua`
fi

# get idcode 
idcode=`cd /usr/lib/lua/dm ; lua /usr/lib/lua/dm/get_idcode.lua`

# get wanip 
wanip=`cd /usr/lib/lua/dm ; lua /usr/lib/lua/dm/get_wan_ip.lua`

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
if [ -z ${url} ]; then
    echo "`date`: perception url is null,now execute lbps routine" >> ${logfile}
    lbps=`cd /usr/lib/lua/dm;/usr/bin/lua /usr/lib/lua/dm/perception_lbps.lua` 
    echo ${lbps} >> ${logfile}
    url=`/sbin/uci get ezwrt.clsconfig.perceptionurl`
fi

# If the websocket client is exist in local host
process=`ps | grep ws_server.py`
result=`echo ${process} | grep -e "python /usr/sbin/ws_server.py*"`

# Launch local websocket client
echo "`date`: pppoeid = ${pppoeid}, password = ${password}, mac = ${mac}, idcode = ${idcode}, wanip = ${wanip}, perceptionurl = ${url}, relogin = ${relogin}" >> ${logfile}
if [ -z "${result}" ] && [ -n "${idcode}" ] && [ -n "${mac}" ]; then
    echo "`date`: Begin to launch websocket client ......" >> ${logfile}
    $python ws_server.py ${pppoeid} ${password} ${mac} ${url} ${idcode} ${wanip}
    echo "`date`: Success to launch websocket client ......" >> ${logfile}
fi

exit 0
