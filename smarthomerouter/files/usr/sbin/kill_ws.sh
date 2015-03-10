#!/bin/sh

ps |grep "ws_serv"|awk '{print $1}'|xargs kill -9
ps |grep "ws_serv"
