import sys
import glob
import argparse
import time
import requests

parser = argparse.ArgumentParser()
parser.add_argument("coordinates", help="The coordinates for the drone to patrol")
parser.add_argument("altitude", help="The altitude at which the drone will patrol")
parser.add_argument("mission_id", help="The mission ID")
parser.add_argument("--drone_id", help="The ID of the drone, default is 2 i.e. the real drone; put 1 for simulator")
parser.add_argument("--ait", help="Set to 1 to make destination ait main gate")
parser.add_argument("--port", help="The port to which the thrift socket must connect. Default is 9090.")
parser.add_argument("--path", help="The complete path of the generated Thrift files. Default is /home/ubuntu/drone-comms/base/gen-py.")
parser.add_argument("--user", help="The user profile name. This will be used in the path to the generated Thrift files. Default is ubuntu.")
args = parser.parse_args()

# Parsing coordinates
# 14.3,23.2 12.3,23.2
print("Parsing coordinates...")
coordinate_list = args.coordinates.split()
print("Parsed coordinate list: {0}".format(coordinate_list))
# ['14.3,23.2', '12.3,23.2']


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

port = 9090
if args.port:
    port = int(args.port)

mission_endpoint = "https://teamdronex.com/api/v1/missions/%s" % mission_id
drone_endpoint = "https://teamdronex.com/api/v1/drone/%s" % drone_id
# sys.path.append('/home/adam/drone/drone-comms/drone/thrift/gen-py')

from drone import Drone
from drone.ttypes import Coordinate

from thrift import Thrift
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol


def main():
    # Make socket
    transport = TSocket.TSocket('localhost', port)

    # Buffering is critical. Raw sockets are very slow
    transport = TTransport.TBufferedTransport(transport)

    # Wrap in a protocol
    protocol = TBinaryProtocol.TBinaryProtocol(transport)

    # Create a client to use the protocol encoder
    client = Drone.Client(protocol)

    # Connect!
    transport.open()

    print("Clearing existing missions...")
    client.clear_missions()

    print("Downloading missions...")
    client.download_missions()

    print("Creating coordinate objects...")
    thrift_coordinate_list = []
    altitude = float(args.altitude)
    for coordinate in coordinate_list:
        latlng = coordinate.split(",")
        lat = latlng[0]
        lng = latlng[1]

        coordinate_obj = Coordinate(latitude=float(lat), longitude=float(lng), altitude=altitude)
        thrift_coordinate_list.append(coordinate_obj)

    print("Sending coordinates to server...")
    client.add_farm_mission(thrift_coordinate_list)
    
    transport.close()

    print("Starting in flight status reports...")
    while(True):
        transport.open()

        print("Reporting flight status...")
        armed = client.report_status(int(args.drone_id))
        if not armed:
            end_mission_status_data = {
                "status": "Done"
            }

            end_drone_status_data = {
                "status": "Available"
            }

            end_mission_post = requests.patch(mission_endpoint, data=end_mission_status_data)

            end_drone_post = requests.patch(drone_endpoint, data=end_drone_status_data)

            client.change_mode("RTL")
            break
        transport.close()
        time.sleep(3)

    # Close!
    transport.close()


if __name__ == '__main__':
    try:
        main()
    except Thrift.TException as tx:
        print("%s" % tx.message)

        error_mission_status_data = {
            "status": "Unable to connect"
        }

        error_drone_status_data = {
            "status": "Unable to connect"
        }

        error_mission_patch = requests.patch(mission_endpoint, data=error_mission_status_data)

        error_drone_patch = requests.patch(drone_endpoint, data=error_drone_status_data)  
        # print(f'{tx.message}')
