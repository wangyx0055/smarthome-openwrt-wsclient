#!/bin/sh

#Param process
relogin=$1
proto=`/sbin/uci get network.wan.proto`

#Log File                                       
logfile=/tmp/ws_client_launch.log

logsize_limits(){                                      
    logsize=`du -k ${logfile}| awk '{print $1}'`
    if [ ${logsize} -ge 1024 ];then                     
	rm -rf ${logfile}                              
    fi                                                 
    return 0
}

while true;
do
	# Delete the logfile if the size of logfile exceed 512K
	logsize_limits

	# Get current wan protocol
        tmpproto=`/sbin/uci get network.wan.proto`
	
	process=`ps | grep ws_server.py`
	result=`echo ${process} | grep -e "python /usr/sbin/ws_server.py*"`
	
	if [ -z "${result}" ] || [ ${proto} != ${tmpproto} ];then
		echo "`date`: websocket client is abnormal, current proto is ${tmpproto}, last proto is ${proto} ">> ${logfile}
		proto=${tmpproto}
		/usr/sbin/ws_kill.sh
		/usr/sbin/ws_start.sh ${relogin} &
	else
		if [ "${relogin}" = "0" ];then
			relogin="1"
		fi
		echo "`date`: websocket client is normal" >> ${logfile}
	fi
	
	sleep 60
done
