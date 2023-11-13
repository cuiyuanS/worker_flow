#! /bin/bash

project_name=worker_flow
user=mei

function gunicorn_file_create() {
    if [ ! -d "$1" ]; then
        mkdir $1
    fi

    if [ $# -gt 1 ] && [ ! -f "$2" ]; then
        touch $2
    fi

    chown -R $user:$user $1
    chmod -R 777 $1
}


gunicorn_log_dir=/var/log/gunicorn
gunicorn_access_file=/var/log/gunicorn/$project_name-access.log
gunicorn_error_file=/var/log/gunicorn/$project_name-error.log
gunicorn_socket_dir=/var/run/gunicorn-socket
gunicorn_pid_dir=/var/run/gunicorn
gunicorn_pid_file=/var/run/gunicorn/$project_name.pid
gunicorn_file_create $gunicorn_log_dir $gunicorn_access_file
gunicorn_file_create $gunicorn_log_dir $gunicorn_error_file
gunicorn_file_create $gunicorn_socket_dir
gunicorn_file_create $gunicorn_pid_dir $gunicorn_pid_file

cd /opt/projects/$project_name

sudo -u $user ./deploy.sh start