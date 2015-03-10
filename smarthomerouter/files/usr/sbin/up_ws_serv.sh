#!/bin/sh

time=`date`
echo $time >> /tmp/time.txt

sn=${1}
mac=${2}

#ip="ws-dev.ezlink-wifi.com"
ip="182.92.232.157"
echo $ip 
#ping -c 3 $ip 
while [ $? == 1 ]
do
    echo "ping test ..."
    ping -c 1 $ip
    echo "ping end"
    sleep 5s
done

process=`ps | grep ws_server.py`
result=`echo ${process} | grep -e "python /usr/sbin/ws_server.py*"`

if [ -z "${result}" ] && [ -n "${sn}" ] && [ -n "${mac}" ]; then
    echo ".......up ws serv success"
    $python ws_server.py ${sn} ${mac} 
    #echo ".......up ws serv success" >> /tmp/time.txt
fi

exit 0
