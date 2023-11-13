#!/bin/bash

# 加载python环境
current_path=$(
  cd $(dirname $0)
  pwd
)
source ~/.bashrc
source $current_path/env/bin/activate

pid_file=/var/run/gunicorn/worker_flow.pid
if [ -e "$pid_file" ]; then
  pid=$(cat $pid_file | tail -1)
  pids=$(ps aux | grep -w $pid | grep -v "grep" | wc -l)
else
  pids=0
fi

case "$1" in
start)
  if [ $pids -gt 0 ]; then
    echo "gunicorn has running!"
    exit 0
  else
    gunicorn manage:app -c $current_path/gunicorn.py
    echo "Start gunicorn service [OK]"
    exit 0
  fi
  ;;
stop)
  if [ $pids -gt 0 ]; then
    kill $pid
    echo "Stop gunicorn service [OK]"
    exit 0
  else
    echo "gunicorn not running"
    exit 0
  fi
  ;;
restart)
  if [ $pids -gt 0 ]; then
    kill -HUP $pid
    echo "restart gunicorn [OK]"
    exit 0
  else
    echo "gunicorn not running"
    echo "Start gunicorn service"
    gunicorn manage:app -c $current_path/gunicorn.py
    echo "Start gunicorn service [OK]"
    exit 0
  fi
  ;;
*)
  echo "Usages: sh deploy.sh [start|stop|restart]"
  ;;
esac
