# py imports
import glob
import sys
import time

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
        print("Downloading missions...")
        self.cmds.download()
        self.cmds.wait_ready()

    def clear_missions(self):
        print("Clearing missions")
        self.cmds.clear()
        self.cmds.upload()

    def download_missions(self):
        print("Downloading missions...")
        self.cmds.download()
        self.cmd.wait_ready()

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
        self.vehicle.mode    = VehicleMode("GUIDED")
        self.vehicle.armed   = True

        # Confirm vehicle armed before attempting to take off
        while not self.vehicle.armed:
            print " Waiting for arming..."
            time.sleep(1)

        print "Taking off!"
        self.vehicle.simple_takeoff(alt) # Take off to target altitude

    def land(self):d
        self.vehicle.mode = VehicleMode("RTL")

    def fly_to(self, lat, lng, alt):d
        if self.vehicle.mode != VehicleMode("GUIDED"):
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
