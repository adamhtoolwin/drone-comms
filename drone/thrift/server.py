# py imports
import glob
import sys
import time
import argparse
import requests
import logging
import datetime

parser = argparse.ArgumentParser()
parser.add_argument("connection", help="The connection type, address and port to be used to the Pixhawk")
parser.add_argument("--port", help="The port at which the thrift socket is to be opened. Default is 9090.")
parser.add_argument("--path", help="The complete path of the generated Thrift files. Default is /home/pi/drone-comms/base/gen-py.")
parser.add_argument("--user", help="The user profile name. This will be used in the path to the generated Thrift files. Default is pi.")
parser.add_argument("--drone_id", help="The ID of the drone, default is 2 i.e. the real drone; put 1 for simulator")
args = parser.parse_args()

logging.basicConfig(filename='mission.log',level=logging.INFO)

if args.path:
    path = args.path
else:
    path = '/home/ubuntu/drone-comms/drone/thrift/gen-py'

if args.user:
    user = args.user
    path = '/home/{}/drone-comms/drone/thrift/gen-py'.format(user)
else:
    user = "ubuntu"

port = 9090
if args.port:
    port = args.port

drone_id = 2
if args.drone_id:
    drone_id = int(args.drone_id)

sys.path.append(path)

# sys.path.append('gen-py')

# Thrift imports
from drone import Drone
from drone.ttypes import Coordinate, Status

from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
from thrift.server import TServer, TNonblockingServer

# Dronekit imports
from dronekit import connect, VehicleMode, Command, LocationGlobalRelative
from pymavlink import mavutil

class DroneHandler:
    def __init__(self):
        self.log = {}

        print("Connecting to vehicle on {0}".format(args.connection))
        self.vehicle = connect(args.connection, wait_ready=True)

        self.cmds = self.vehicle.commands

        self.clear_missions()

        self.download_missions()

        time.sleep(2)

        # self.fixed_home_location = {
        #     "latitude": self.vehicle.home_location.lat,
        #     "longitude": self.vehicle.home_location.lon,
        # }
        # print("First home location: {0},{1}".format(self.fixed_home_location["latitude"],self.fixed_home_location["longitude"]))

        self.report_status(drone_id)

        msg = self.vehicle.message_factory.command_long_encode(
            0, 0,    # target_system, target_component
            mavutil.mavlink.MAV_CMD_DO_SET_SERVO, #command
            0, #confirmation
            5,    # param 1, yaw in degrees
            1900,          # param 2, yaw speed deg/s
            0,          # param 3, direction -1 ccw, 1 cw
            0, # param 4, relative offset 1, absolute angle 0
            0, 0, 0)    # param 5 ~ 7 not used
            
        # send command to vehicle
        self.vehicle.send_mavlink(msg)

    def check_status(self):
        print("Arming...")
        if self.vehicle.armed == False:
            self.vehicle.armed = True

        self.report_status(drone_id)

    def start_camera(self):
        print("Starting Camera")

    def arm(self):
        if self.vehicle.armed == False:
            self.vehicle.armed = True

        self.report_status(drone_id)

    def disarm(self):
        if self.vehicle.armed == True:
            self.vehicle.armed = False
        
        self.report_status(drone_id)

    def report_status(self, drone_id):
        # Can call from client loop there?
        
        # Get some vehicle attributes (state)
        print "Autopilot Firmware version: %s" % self.vehicle.version
        print "Autopilot capabilities (supports ftp): %s" % self.vehicle.capabilities.ftp
        print ("Home Location: %s" % self.vehicle.home_location)
        print "Global Location: %s" % self.vehicle.location.global_frame
        print "Global Location (relative altitude): %s" % self.vehicle.location.global_relative_frame
        print "Local Location: %s" % self.vehicle.location.local_frame    #NED
        print "Attitude: %s" % self.vehicle.attitude
        print "Velocity: %s" % self.vehicle.velocity
        print "GPS: %s" % self.vehicle.gps_0
        print "Groundspeed: %s" % self.vehicle.groundspeed
        print "Airspeed: %s" % self.vehicle.airspeed
        print "Gimbal status: %s" % self.vehicle.gimbal
        print "Battery: %s" % self.vehicle.battery
        print "EKF OK?: %s" % self.vehicle.ekf_ok
        print "Last Heartbeat: %s" % self.vehicle.last_heartbeat
        print "Rangefinder: %s" % self.vehicle.rangefinder
        print "Rangefinder distance: %s" % self.vehicle.rangefinder.distance
        print "Rangefinder voltage: %s" % self.vehicle.rangefinder.voltage
        print "Heading: %s" % self.vehicle.heading
        print "Is Armable?: %s" % self.vehicle.is_armable
        print "System status: %s" % self.vehicle.system_status.state
        print "Mode: %s" % self.vehicle.mode.name    # settable
        print "Armed: %s" % self.vehicle.armed    # settable
        print("")
        


        print("Sending one time status to server...\n")

        nav_log = {
            "gps_latitude": self.vehicle.location.global_relative_frame.lat,
            "gps_longitude": self.vehicle.location.global_relative_frame.lon,
            "altitude": self.vehicle.location.global_relative_frame.alt,
            "battery_voltage": self.vehicle.battery.voltage,
            "battery_level": self.vehicle.battery.level,
            "battery_current": self.vehicle.battery.current,
            "ekf_ok": self.vehicle.ekf_ok,
            "is_armable": self.vehicle.is_armable,
            "system_status": self.vehicle.system_status.state,
            "mode": self.vehicle.mode.name,
            "armed": self.vehicle.armed,
            "drone_id": drone_id,
        }

        nav_post = requests.post("https://teamdronex.com/api/v1/nav_logs", data=nav_log)

        armed = self.vehicle.armed
        gps_latitude = self.vehicle.location.global_relative_frame.lat
        gps_longitude = self.vehicle.location.global_relative_frame.lon
        altitude = self.vehicle.location.global_relative_frame.alt
        retrieved_date = datetime.datetime.now()

        status_obj = Status(armed=armed, latitude=float(gps_latitude), longitude=float(gps_longitude), altitude=altitude, datetime=retrieved_date)

        return status_obj

    def clear_missions(self):
        print("Clearing missions")
        self.cmds.clear()
        self.cmds.upload()

    def download_missions(self):
        print("Downloading missions...")
        self.cmds.download()
        self.cmds.wait_ready()

    def add_waypoint(self, latitude, longitude, alt):
        cmd = Command(0,0,0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, 0, 0, 0, 0, 0, 0, latitude, longitude, alt)
        self.cmds.add(cmd)

    def add_farm_mission(self, coordinate_list):
        self.clear_missions()
        self.download_missions()

        starting_lat = self.vehicle.location.global_relative_frame.lat
        starting_lon = self.vehicle.location.global_relative_frame.lon

        first_lat = coordinate_list[0].latitude
        first_lon = coordinate_list[0].longitude
        starting_alt = coordinate_list[0].altitude

        for count, coordinate in enumerate(coordinate_list):
            lat = coordinate.latitude
            lng = coordinate.longitude
            alt = coordinate.altitude
            print("Coordinate {0}: {1},{2},{3}".format(count, lat, lng, alt))

            # Create mission for point
            cmd = Command(0,0,0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, 0, 0, 0, 0, 0, 0, lat, lng, alt)
            self.cmds.add(cmd)

        # Add final waypoint to first point
        return_to_first_wp_cmd = Command(0,0,0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, 0, 0, 0, 0, 0, 0, first_lat, first_lon, starting_alt)
        return_to_home_cmd = Command(0,0,0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,mavutil.mavlink.MAV_CMD_NAV_RETURN_TO_LAUNCH, 0, 0, 0, 0, 0, 0, 0, 0, 0)
        
        # return_to_home_cmd = Command(0,0,0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, 0, 0, 0, 0, 0, 0, starting_lat, starting_lon, starting_alt)
        # land_cmd = Command(0,0,0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, 0, 0, 0, 0, 0, 0, starting_lat, starting_lon, starting_alt)        
        
        self.cmds.add(return_to_first_wp_cmd)
        self.cmds.add(return_to_home_cmd)

        print("Uploading missions...")
        self.cmds.upload()
        self.cmds.wait_ready()

        self.takeoff(starting_alt)

        self.change_mode("AUTO")

    def add_delivery_mission(self, dest_latitude, dest_longitude, alt):
        logging.info('Mission parameters received')
        self.clear_missions()
        self.download_missions()
        
        # Store first location to return cuz home location is dangerous
        # NO MORE DANGER
        # starting_lat = self.vehicle.location.global_relative_frame.lat
        # starting_lon = self.vehicle.location.global_relative_frame.lon

        # cmd1 = Command(0,0,0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,mavutil.mavlink.MAV_CMD_NAV_TAKEOFF, 0, 0, 0, 0, 0, 0, 0, 0, alt)
        cmd1 = Command(0,0,0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, 0, 0, 0, 0, 0, 0, dest_latitude, dest_longitude, alt)
        cmd2 = Command(0,0,0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, 0, 0, 0, 0, 0, 0, dest_latitude, dest_longitude, 5)
        cmd3 = Command(0,0,0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,mavutil.mavlink.MAV_CMD_DO_SET_SERVO, 0, 0, 5, 1900, 0, 0, 0, 0, 0)
        cmd4 = Command(0,0,0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, 0, 0, 0, 0, 0, 0, dest_latitude, dest_longitude, alt)
        cmd5 = Command(0,0,0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,mavutil.mavlink.MAV_CMD_NAV_RETURN_TO_LAUNCH, 0, 0, 0, 0, 0, 0, 0, 0, 0)
        # cmd4 = Command(0,0,0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,mavutil.mavlink.MAV_CMD_MISSION_START, 0, 0, 0, 0, 0 , 0, 0, 0, 0)
        
        # Add and send commands
        self.cmds.add(cmd1)
        self.cmds.add(cmd2)
        self.cmds.add(cmd3)
        self.cmds.add(cmd4)
        self.cmds.add(cmd5)

        # self.cmds.add(cmd3)
        
        print("Uploading missions...")
        self.cmds.upload()
        self.cmds.wait_ready()

        # print("Taking off to {0}".format(str(alt)))
        self.takeoff(alt)

        self.change_mode("AUTO")

    def change_mode(self, mode):
        print("Changing mode from {0} to {1}...".format(self.vehicle.mode.name, mode))
        self.vehicle.mode = VehicleMode(mode)
    
    def takeoff(self, alt):
        print "Basic pre-arm checks"
        # Don't try to arm until autopilot is ready
        while not self.vehicle.is_armable:
            print "Waiting for vehicle to initialise..."
            time.sleep(1)

        print "Arming motors"
        # Copter should arm in GUIDED mode
        self.vehicle.mode = VehicleMode("GUIDED")
        self.vehicle.armed = True

        # Confirm vehicle armed before attempting to take off
        count = 0
        while not self.vehicle.armed:
            print " Waiting for arming..."
            count = count + 1
            if count > 5:
                drone_endpoint = "https://teamdronex.com/api/v1/drone/%s" % drone_id

                error_drone_status_data = {
                    "status": "Unable to arm"
                }

                error_drone_patch = requests.patch(drone_endpoint, data=error_drone_status_data) 
                return
            
            time.sleep(1)

        print("Taking off to {0}...".format(str(alt)))
        self.vehicle.simple_takeoff(alt) # Take off to target altitude

        while(True):
            if self.vehicle.location.global_relative_frame.alt>=alt*0.95:
                print "Reached target altitude."
                break
            time.sleep(1)

    def land(self):
        self.vehicle.mode = VehicleMode("LAND")

    def fly_to(self, lat, lng, alt):
        print ("Flying away...")
        if self.vehicle.mode != VehicleMode("GUIDED"):
            print("Changing mode to GUIDED")
            self.vehicle.mode = VehicleMode("GUIDED")  

        location = LocationGlobalRelative(lat, lng, alt)
        self.vehicle.simple_goto(location)


if __name__ == '__main__':
    handler = DroneHandler()
    processor = Drone.Processor(handler)
    transport = TSocket.TServerSocket(host='0.0.0.0', port=port)
    tfactory = TTransport.TBufferedTransportFactory()
    pfactory = TBinaryProtocol.TBinaryProtocolFactory()

    server = TServer.TSimpleServer(processor, transport, tfactory, pfactory)

    print('Starting the server...')
    server.serve()
    print('done.')
