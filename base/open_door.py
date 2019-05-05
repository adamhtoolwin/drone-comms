import sys
import glob
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--path", help="The complete path of the generated Thrift files. Default is /home/ubuntu/drone-comms/base/gen-py.")
parser.add_argument("--port", help="The port through which the client should connect to the server. Default is 8080.")

args = parser.parse_args()

port = 8081
if args.port:
    port = args.port

path = '/home/pi/drone-comms/base/gen-py'
if args.path:
    path = args.path


sys.path.append(path)

# sys.path.append('/home/adam/drone/drone-comms/base/gen-py')

from base import BaseDoor

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
    client = BaseDoor.Client(protocol)

    # Connect!
    transport.open()

    client.openDoor()
    print('Open Sesame')

    # Close!
    transport.close()


if __name__ == '__main__':
    try:
        main()
    except Thrift.TException as tx:
        print("%s" % tx.message)
        # print(f'{tx.message}')
