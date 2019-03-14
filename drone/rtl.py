"""
Clears missions and RTLs the drone.
"""
from dronekit import connect, VehicleMode, Command
from pymavlink import mavutil
import time
import argparse
import requests

# Parsing args
parser = argparse.ArgumentParser()
parser.add_argument("connection", help="The connection string to be used, i.e. the Pixhawk")
parser.add_argument("--drone_id", help="The ID of the drone, default is 1 i.e. the real drone; put 2 for simulator")
args = parser.parse_args()

if args.drone_id:
    drone_id = args.drone_id
else:
    drone_id = 1

# Connect to the Vehicle.
print("Connecting to vehicle on: %s" % (args.connection,))
vehicle = connect(args.connection, wait_ready=True)

# Download missions from Pixhawk
print("Downloading missions")
cmds = vehicle.commands
cmds.download()
cmds.wait_ready()

# Save the vehicle commands to a list
missionlist=[]
for cmd in cmds:
    missionlist.append(cmd)

print("Mission List: %s" % missionlist)

cmds.clear()
cmds.upload()
print("")
time.sleep(1)

vehicle.mode = VehicleMode("RTL")
time.sleep(1)

# Close vehicle object before exiting script
vehicle.close()