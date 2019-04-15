# py imports
import glob
import sys
import time
import argparse
import requests

parser = argparse.ArgumentParser()
parser.add_argument("connection", help="The connection type, address and port to be used to the Pixhawk")
parser.add_argument("--port", help="The port at which the thrift socket is to be opened. Default is 9090.")
parser.add_argument("--path", help="The complete path of the generated Thrift files. Default is /home/pi/drone-comms/base/gen-py.")
parser.add_argument("--user", help="The user profile name. This will be used in the path to the generated Thrift files. Default is pi.")
args = parser.parse_args()

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

sys.path.append(path)

# sys.path.append('gen-py')

# Thrift imports
from drone import Drone

from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
from thrift.server import TServer

# Dronekit imports
from dronekit import connect, VehicleMode, Command, LocationGlobalRelative
from pymavlink import mavutil

class DroneHandler:
    def __init__(self):
        self.log = {}

        print("Connecting to vehicle on {0}".format(args.connection))
        self.vehicle = connect(args.connection, wait_ready=True)

        self.cmds = self.vehicle.commands

        self.download_missions()

        self.report_status(1)

    def report_status(self, drone_id):
        # Can call from client loop there?
        armed = self.vehicle.armed

        print("Sending one time status to server...")

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
            "armed": armed,
            "drone_id": drone_id,
        }

        nav_post = requests.post("https://teamdronex.com/api/v1/nav_logs", data=nav_log)

        return armed

        ### Temporarily removed loop in server function
        # while(True):
        #     print("Sending status to server...")

        #     nav_log = {
        #         "gps_latitude": self.vehicle.location.global_relative_frame.lat,
        #         "gps_longitude": self.vehicle.location.global_relative_frame.lon,
        #         "altitude": self.vehicle.location.global_relative_frame.alt,
        #         "battery_voltage": self.vehicle.battery.voltage,
        #         "battery_level": self.vehicle.battery.level,
        #         "battery_current": self.vehicle.battery.current,
        #         "ekf_ok": self.vehicle.ekf_ok,
        #         "is_armable": self.vehicle.is_armable,
        #         "system_status": self.vehicle.system_status.state,
        #         "mode": self.vehicle.mode.name,
        #         "armed": self.vehicle.armed,
        #         "drone_id": drone_id,
        #     }

        #     nav_post = requests.post("https://teamdronex.com/api/v1/nav_logs", data=nav_log)

        #     time.sleep(3)
        ###

    def clear_missions(self):
        print("Clearing missions")
        self.cmds.clear()
        self.cmds.upload()

    def download_missions(self):
        print("Downloading missions...")
        self.cmds.download()
        self.cmds.wait_ready()

    def add_delivery_mission(self, dest_latitude, dest_longitude, alt):
        # cmd1 = Command(0,0,0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,mavutil.mavlink.MAV_CMD_NAV_TAKEOFF, 0, 0, 0, 0, 0, 0, 0, 0, alt)
        cmd1 = Command(0,0,0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, 0, 0, 0, 0, 0, 0, dest_latitude, dest_longitude, alt)
        cmd2 = Command(0,0,0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, 0, 0, 0, 0, 0, 0, self.vehicle.home_location.lat, self.vehicle.home_location.lon, alt)
        cmd3 = Command(0,0,0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,mavutil.mavlink.MAV_CMD_NAV_RETURN_TO_LAUNCH, 0, 0, 0, 0, 0, 0, 0, 0, 0)
        # cmd4 = Command(0,0,0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,mavutil.mavlink.MAV_CMD_MISSION_START, 0, 0, 0, 0, 0 , 0, 0, 0, 0)
        
        # Add and send commands
        self.cmds.add(cmd1)
        self.cmds.add(cmd2)
        self.cmds.add(cmd3)
        
        print("Uploading missions")
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
        while not self.vehicle.armed:
            print " Waiting for arming..."
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
