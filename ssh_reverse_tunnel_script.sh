#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin

ssh -i /home/pi/dronetracker.pem -f -N -T -R 2019:localhost:22 webserver-aws
ssh -i /home/pi/dronetracker.pem -f -N -T -R 9091:localhost:9090 webserver-aws

