"""
Script to list all params in drone
"""

from dronekit import connect, VehicleMode, Command
from pymavlink import mavutil
import time
import argparse
import requests

# Parsing args
parser = argparse.ArgumentParser()
parser.add_argument("connection", help="The connection string to be used, i.e. the Pixhawk")
args = parser.parse_args()

# Connect to drone
vehicle = connect(args.connection, wait_ready=True)

# Get all params
print ("\nPrint all parameters (iterate `vehicle.parameters`):")
for key, value in vehicle.parameters.iteritems():
    print ("Key:%s Value:%s") % (key,value)
