import sys
import glob
import argparse
import time
import requests

parser = argparse.ArgumentParser()
parser.add_argument("latitude", help="The latitude of the destination")
parser.add_argument("longitude", help="The longitude of the destination")
parser.add_argument("altitude", help="The altitude at which the drone will fly")
parser.add_argument("mission_id", help="The longitude of the destination")
parser.add_argument("--drone_id", help="The ID of the drone, default is 2 i.e. the real drone; put 1 for simulator")
parser.add_argument("--ait", help="Set to 1 to make destination ait main gate")
parser.add_argument("--port", help="The port to which the thrift socket must connect. Default is 9090.")
parser.add_argument("--path", help="The complete path of the generated Thrift files. Default is /home/ubuntu/drone-comms/base/gen-py.")
parser.add_argument("--user", help="The user profile name. This will be used in the path to the generated Thrift files. Default is ubuntu.")
args = parser.parse_args()

# TODO
if args.ait:
    dest_latitude = 14.076550
    dest_longitude = 100.614012
#

# Need mission id for specifying when mission done
mission_id = args.mission_id

drone_id = 2
if args.drone_id:
    drone_id = args.drone_id

if args.path:
    path = args.path
else:
    path = '/home/ubuntu/drone-comms/drone/thrift/gen-py'

if args.user:
    user = args.user
    path = '/home/{}/drone-comms/drone/thrift/gen-py'.format(user)

else:
    user = "ubuntu"

sys.path.append(path)

# port = 9090
if args.port:
    port = args.port
else:
    port = 9090

# sys.path.append('/home/adam/drone/drone-comms/drone/thrift/gen-py')

from drone import Drone

from thrift import Thrift
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol


def main():
    # Make socket
    transport = TSocket.TSocket('localhost', 9090)

    # Buffering is critical. Raw sockets are very slow
    transport = TTransport.TBufferedTransport(transport)

    # Wrap in a protocol
    protocol = TBinaryProtocol.TBinaryProtocol(transport)

    # Create a client to use the protocol encoder
    client = Drone.Client(protocol)

    # Connect!
    transport.open()

    dest_latitude = float(args.latitude)
    dest_longitude = float(args.longitude)
    altitude = float(args.altitude)

    print("Clearing existing missions...")
    client.clear_missions()

    print("Downloading missions...")
    client.download_missions()

    print("Add mission to {0}, {1} at {2} metres".format(args.latitude, args.longitude, args.altitude))
    client.add_delivery_mission(dest_latitude, dest_longitude, altitude)

    # client.fly_to(14.076550, 100.614012, 50)

    print("Starting in flight status reports...")
    while(True):
        print("Reporting flight status...")
        armed = client.report_status(int(args.drone_id))
        if not armed:
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
        
        time.sleep(3)

    # Close!
    transport.close()


if __name__ == '__main__':
    try:
        main()
    except Thrift.TException as tx:
        print("%s" % tx.message)
        # print(f'{tx.message}')
