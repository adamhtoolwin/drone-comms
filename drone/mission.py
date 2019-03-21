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
        nav_log = {
            "gps_latitude": vehicle.location.global_relative_frame.lat,
            "gps_longitude": vehicle.location.global_relative_frame.lon,
            "altitude": vehicle.location.global_relative_frame.alt,
            "battery": vehicle.battery.voltage,
            "drone_id": drone_id,
        }

        nav_post = requests.post(server_address, data=nav_log)

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
parser.add_argument("mission_id", help="The longitude of the destination")
parser.add_argument("--groundspeed", help="The default groundspeed of the drone")
parser.add_argument("--server", help="The address of the REST server")
parser.add_argument("--drone_id", help="The ID of the drone, default is 1 i.e. the real drone; put 2 for simulator")
args = parser.parse_args()

if args.drone_id:
    drone_id = args.drone_id
else:
    drone_id = 1

dest_latitude = float(args.latitude)
dest_longitude = float(args.longitude)

if args.server:
    # for dev - specify address
    server_address = args.server
else:
    # for prod
    server_address = "https://teamdronex.com/api/v1/nav_logs"

# Need mission id for specifying when mission done
mission_id = args.mission_id

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

# Need to re download missions before getting home location
cmds = vehicle.commands
cmds.download()
cmds.wait_ready()
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
cmd1 = Command(0,0,0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, 0, 0, 0, 0, 0, 0, dest_latitude, dest_longitude, 20)
cmd2 = Command(0,0,0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, 0, 0, 0, 0, 0, 0,vehicle.home_location.lat, vehicle.home_location.lon, 20)
cmd3 = Command(0,0,0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,mavutil.mavlink.MAV_CMD_NAV_RETURN_TO_LAUNCH, 0, 0, 0, 0, 0, 0, 0, 0, 0)
cmd4 = Command(0,0,0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,mavutil.mavlink.MAV_CMD_MISSION_START, 0, 0, 0, 0, 0, 0, 0, 0, 0)

# Add and send commands
cmds.add(cmd1)
cmds.add(cmd2)
cmds.add(cmd3)
print("Uploading missions")
cmds.upload()

# POST initial location to server
init_nav = {
    "gps_latitude": vehicle.location.global_relative_frame.lat,
    "gps_longitude": vehicle.location.global_relative_frame.lon,
    "altitude": vehicle.location.global_relative_frame.alt,
    "drone_id": drone_id,
}

## local dev address
## "http://localhost:3000/api/v1/nav_logs"
init_nav_post = requests.post(server_address, data=init_nav)

arm_and_takeoff(20)

time.sleep(2)

# Change mode to AUTO to execute mission plan
vehicle.mode = VehicleMode("AUTO")

while True:
    nav_logs = {
        "gps_latitude": vehicle.location.global_relative_frame.lat,
        "gps_longitude": vehicle.location.global_relative_frame.lon,
        "altitude": vehicle.location.global_relative_frame.alt,
        "battery": vehicle.battery.voltage,
        "drone_id": drone_id,
    }

    print("")
    print("Posting with this navlog")
    print(nav_logs)
    print("")

    print("Posting navlogs to %s" % server_address)

    nav_post = requests.post(server_address, data=nav_logs)

    print("")

    # Hold for 5 seconds
    print("Waiting for 5 seconds")
    time.sleep(2)

    # break if disarmed
    if vehicle.armed == False:
        end_mission_status_data = {
            "status": "Done"
        }

        end_drone_status_data = {
            "status": "Available"
        }

        mission_endpoint = "https://teamdronex.com/api/v1/missions/%s" % mission_id
        end_mission_post = requests.patch(mission_endpoint, data=end_mission_status_data)

        drone_endpoint = "https://teamdronex.com/api/v1/drone/%s" % drone_id
        end_drone_post = requests.patch(drone_endpoint, data=end_drone_status_data)
        break

time.sleep(2)

end_mission = {

}

# Close vehicle object before exiting script
vehicle.close()