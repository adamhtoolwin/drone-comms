#!/bin/bash
ssh -i ~/dronetracker.pem -f -N -T -R 2019:localhost:22 webserver-aws

