#!/bin/bash
PATH=/home/pi/.pyenv/shims:/home/pi/.pyenv/bin:/home/pi/.rbenv/plugins/ruby-build/bin:/home/pi/.rbenv/shims:/home/pi/.rbenv/bin:/home/pi/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games:/snap/bin:/home/pi/.local/bin

python ~/drone-comms/drone/thrift/server.py udp:192.168.4.2:14550 --user pi --drone_id 2