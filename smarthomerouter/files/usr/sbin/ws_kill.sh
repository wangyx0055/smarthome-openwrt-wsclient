#!/bin/sh

ps |grep "ws_start"|awk '{print $1}'|xargs kill -9
ps |grep "ws_server"|awk '{print $1}'|xargs kill -9
