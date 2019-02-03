"""
This script simply arms the vehicle and then disarms after 5 seconds.
"""
from dronekit import connect, VehicleMode
import time
import argparse

# Parsing args
parser = argparse.ArgumentParser()
parser.add_argument("connection", help="The connection string to be used, i.e. the Pixhawk")
parser.add_argument("--airspeed", help="The default airspeed of the drone")
args = parser.parse_args()

# Connect to the Vehicle.
print("Connecting to vehicle on: %s" % (args.connection,))
vehicle = connect(args.connection, wait_ready=True)

# Set the default vehicle airspeed
if args.airspeed:
    vehicle.airspeed = int(args.airspeed)
else:
    vehicle.groundspeed = 3 ####TODO
print("Setting the default airspeed to %s" % vehicle.airspeed)

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

print("")


# Get some vehicle attributes (state)
print "Autopilot Firmware version: %s" % vehicle.version
print "Autopilot capabilities (supports ftp): %s" % vehicle.capabilities.ftp
print ("Home Location: %s" % vehicle.home_location)
print "Global Location: %s" % vehicle.location.global_frame
print "Global Location (relative altitude): %s" % vehicle.location.global_relative_frame
print "Local Location: %s" % vehicle.location.local_frame    #NED
print "Attitude: %s" % vehicle.attitude
print "Velocity: %s" % vehicle.velocity
print "GPS: %s" % vehicle.gps_0
print "Groundspeed: %s" % vehicle.groundspeed
print "Airspeed: %s" % vehicle.airspeed
print "Gimbal status: %s" % vehicle.gimbal
print "Battery: %s" % vehicle.battery
print "EKF OK?: %s" % vehicle.ekf_ok
print "Last Heartbeat: %s" % vehicle.last_heartbeat
print "Rangefinder: %s" % vehicle.rangefinder
print "Rangefinder distance: %s" % vehicle.rangefinder.distance
print "Rangefinder voltage: %s" % vehicle.rangefinder.voltage
print "Heading: %s" % vehicle.heading
print "Is Armable?: %s" % vehicle.is_armable
print "System status: %s" % vehicle.system_status.state
print "Mode: %s" % vehicle.mode.name    # settable
print "Armed: %s" % vehicle.armed    # settable

print("")

# Arming the vehicle
print("Arming the vehicle")  
vehicle.armed = True
print "Armed: %s" % vehicle.armed  

time.sleep(10)

# Disarming the vehicle
print("Disarming the vehicle")
vehicle.armed = False
print "Armed: %s" % vehicle.armed    # settable

# Close vehicle object before exiting script
vehicle.close()