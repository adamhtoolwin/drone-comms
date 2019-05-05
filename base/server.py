import glob
import sys

sys.path.append('gen-py')

from base import BaseDoor

from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
from thrift.server import TServer


class BaseHandler:
    def __init__(self):
        self.log = {}

        self.openDoor()

        self.closeDoor()
    
    def openDoor(self):
        print("HELLO")

        import RPi.GPIO as GPIO
        import time
        import sys
        IN1 = 27
        IN2 = 22
        IN3 = 23
        IN4 = 24
        ENA = 18
        ENB = 12

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(IN1, GPIO.OUT)
        GPIO.setup(IN2, GPIO.OUT)
        GPIO.setup(IN3, GPIO.OUT)
        GPIO.setup(IN4, GPIO.OUT)
        GPIO.setup(ENA, GPIO.OUT)
        GPIO.setup(ENB, GPIO.OUT)
        p=GPIO.PWM(ENA,3450)
        s=GPIO.PWM(ENB,3450)
        p.start(100)
        s.start(100)

        def forward(tf):

            GPIO.output(IN1, GPIO.HIGH)
            GPIO.output(IN2, GPIO.LOW)
            GPIO.output(IN3, GPIO.HIGH)
            GPIO.output(IN4, GPIO.LOW)
            time.sleep(tf)
            #GPIO.cleanup()
            
        print("open")
        forward(1.5)
        GPIO.cleanup()

    def closeDoor(self):
        print("Closing door...")
        import RPi.GPIO as GPIO
        import time
        import sys
        IN1 = 27
        IN2 = 22
        IN3 = 23
        IN4 = 24
        ENA = 18
        ENB = 12

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(IN1, GPIO.OUT)
        GPIO.setup(IN2, GPIO.OUT)
        GPIO.setup(IN3, GPIO.OUT)
        GPIO.setup(IN4, GPIO.OUT)
        GPIO.setup(ENA, GPIO.OUT)
        GPIO.setup(ENB, GPIO.OUT)
        p=GPIO.PWM(ENA,3450)
        s=GPIO.PWM(ENB,3450)
        p.start(100)
        s.start(100)

        def reverse(tf):
            GPIO.output(IN1, GPIO.LOW)
            GPIO.output(IN2, GPIO.HIGH)
            GPIO.output(IN3, GPIO.LOW)
            GPIO.output(IN4, GPIO.HIGH)
            time.sleep(tf)
            #GPIO.cleanup()

        print("close")
        reverse(1.5)
        GPIO.cleanup()


if __name__ == '__main__':
    handler = BaseHandler()
    processor = BaseDoor.Processor(handler)
    transport = TSocket.TServerSocket(host='0.0.0.0', port=8080)
    tfactory = TTransport.TBufferedTransportFactory()
    pfactory = TBinaryProtocol.TBinaryProtocolFactory()

    server = TServer.TSimpleServer(processor, transport, tfactory, pfactory)

    print('Starting the server...')
    server.serve()
    print('done.')
