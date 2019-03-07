"""
"""
from dronekit import connect, VehicleMode, Command
from pymavlink import mavutil
import time
import argparse
import requests

def arm_and_takeoff(aTargetAltitude):
    """
    Arms vehicle and fly to aTargetAltitude.
    """

    print "Basic pre-arm checks"
    # Don't try to arm until autopilot is ready
    while not vehicle.is_armable:
        print " Waiting for vehicle to initialise..."
        time.sleep(1)

    print "Arming motors"
    # Copter should arm in GUIDED mode
    vehicle.mode    = VehicleMode("GUIDED")
    vehicle.armed   = True

    # Confirm vehicle armed before attempting to take off
    while not vehicle.armed:
        print " Waiting for arming..."
        time.sleep(1)

    print "Taking off!"
    vehicle.simple_takeoff(aTargetAltitude) # Take off to target altitude

    # Wait until the vehicle reaches a safe height before processing the goto (otherwise the command
    #  after Vehicle.simple_takeoff will execute immediately).
    while True:
        print " Altitude: ", vehicle.location.global_relative_frame.alt
        #Break and return from function just below target altitude.
        if vehicle.location.global_relative_frame.alt>=aTargetAltitude*0.95:
            print "Reached target altitude"
            break
        time.sleep(1)

# Parsing args
parser = argparse.ArgumentParser()
parser.add_argument("connection", help="The connection string to be used, i.e. the Pixhawk")
parser.add_argument("latitude", help="The latitude of the destination")
parser.add_argument("longitude", help="The longitude of the destination")
parser.add_argument("--groundspeed", help="The default groundspeed of the drone")
args = parser.parse_args()

dest_latitude = float(args.latitude)
dest_longitude = float(args.longitude)

# Connect to the Vehicle.
print("Connecting to vehicle on: %s" % (args.connection,))
vehicle = connect(args.connection, wait_ready=True)

# Set the default vehicle airspeed
if args.groundspeed:
    vehicle.groundspeed = int(args.groundspeed)
else:
    vehicle.groundspeed = 5 ####TODO
print("Setting the default groundspeed to %s" % vehicle.groundspeed)

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

cmds = vehicle.commands
vehicle.mode = VehicleMode("STABILIZE")
time.sleep(1)

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


time.sleep(2)

print("")
print("Destination latitude: %s" % dest_latitude)
print("Destination longitude: %s" % dest_longitude)
print("")

# Preset command
# cmd1 = Command(0,0,0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,mavutil.mavlink.MAV_CMD_NAV_TAKEOFF, 0, 0, 0, 0, 0, 0,vehicle.location.global_relative_frame.lat,vehicle.location.global_relative_frame.lon, 20)
cmd2 = Command(0,0,0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, 0, 0, 0, 0, 0, 0, dest_latitude, dest_longitude, 20)
cmd3 = Command(0,0,0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, 0, 0, 0, 0, 0, 0,vehicle.home_location.lat, vehicle.home_location.lon, 20)
cmd4 = Command(0,0,0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,mavutil.mavlink.MAV_CMD_NAV_RETURN_TO_LAUNCH, 0, 0, 0, 0, 0, 0, 0, 0, 0)
cmd5 = Command(0,0,0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,mavutil.mavlink.MAV_CMD_MISSION_START, 0, 0, 0, 0, 0, 0, 0, 0, 0)

# Add and send commands
# cmds.add(cmd1)
cmds.add(cmd2)
cmds.add(cmd3)
cmds.add(cmd4)
print("Uploading missions")
cmds.upload()

arm_and_takeoff(20)

time.sleep(2)
vehicle.mode = VehicleMode("AUTO")

while True:
    nav_logs = {
        "gps_latitude": vehicle.location.global_relative_frame.lat,
        "gps_longitude": vehicle.location.global_relative_frame.lon,
        "altitude": vehicle.location.global_relative_frame.alt,
        "drone_id": 2,
    }

    print("")
    print("Posting with this navlog")
    print(nav_logs)
    print("")

    print("Posting navlogs")

    nav_post = requests.post("http://localhost:3000/api/v1/nav_logs", data=nav_logs)

    print("")

    # Hold for 5 seconds
    print("Waiting for 5 seconds")
    time.sleep(5)

    if vehicle.armed == False:
        break

time.sleep(2)

# Close vehicle object before exiting script
vehicle.close()