#!/bin/bash

kill -9 `ps -ef | grep server.py | grep -v grep | awk '{print $2}'`

rm -rf ./tmp/

[ ! -d ./log ] && mkdir ./log
[ ! -d ./tmp ] &&  mkdir ./tmp

thetime=`date +%Y-%m-%d--%H-%M-%S`

[ -f ./log/error.log ] && mv ./log/error.log "./log/$thetime-error.log"
[ -f ./log/server.log ] && mv ./log/server.log "./log/$thetime-server.log"

nohup python server.py 2>> ./log/error.log >> ./log/server.log &
