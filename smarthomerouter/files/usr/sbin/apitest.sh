#!/bin/sh
set +v
set +x

if [[ "$1" = "" ]]; then
    echo "apitest [auth/net/sys/info] [method] [para1] [para2] ..."
    exit
fi

echo -e "\n\n"

ip="127.0.0.1"
echo "ip is : "$ip

apiclass=$1
echo "apiclass is : "$apiclass
shift

method=$1
echo "method is : "$method
shift

token="myluckday"

while [ $# -ne 0 ]
do
    arg=`echo $1`
    params+="\"$arg\""
    if [ $# -gt 1 ]; then
        params+=","
    fi
    shift
done
echo "params list : "$params

echo -e "\n\n"

set -x
result=`curl -s -i -X POST -d "{\"id\":\"$method\",\"method\":\"$method\",\"params\":[$params]}" http://$ip/cgi-bin/luci/api/$apiclass?auth=$token`
set +x

echo -e "\n\n"
#echo $result 2>&1

exit 0






