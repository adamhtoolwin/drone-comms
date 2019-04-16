#!/bin/bash
ssh -i ~/dronetracker.pem -f -N -T -R 2019:localhost:22 webserver-aws
ssh -i ~/dronetracker.pem -f -N -T -R 9091:localhost:9090 webserver-aws

