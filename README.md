# drone-comms
A testbed for drone-server communications

## Starting the simulator
### Dronekit
home location - 14.079140, 100.609484

Run ```dronekit-sitl copter --home=14.079140,100.609484,584,353```

This runs the SITL sim on port 5760 with the specified home location(lat,lng,alt,yaw).

**(IMPORTANT)** There is a version conflict for pymavlink with the dronekit sim (**2.0.6**) and mavproxy (**2.3.4**). A workaround is to

1. Install the reqs for dronekit sim - ```pip install dronekit-sitl```
2. Install the reqs for mavproxy - ```pip install MAVProxy```

### Ardupilot
TODO


## Scripts

**(IMPORTANT)** Requirements: Python 2.7

Pip packages: dronekit, dronekit-sitl(optional), MAVProxy

### hello-drone.py
Run ```python hello-drone.py --connection_string--``` to get a basic status message.

The ```connection_string``` can be USB, serial or network.

For example: ```python hello-drone.py tcp:127.0.0.1:5760``` will connect to a SITL simulator running at port TCP 5760 on the local machine. 

### mission.py

Run ```python mission.py --connection_string-- --lattitude-- --longitude-- --drone_id--``` to execute a mission to the specified destination.

The ```connection_string``` can be USB, serial or network.

#### CLI Arguments
1. connection_string
2. latitude
3. longitude
4. drone_id (optional)(default=1)
This is to specify to use the simultor(id=2) or the real drone(id=1).

**```python mission.py --help```** for more info.

### For use with GCS (Mission Planner) **and** the script

```mavproxy.py --master tcp:127.0.0.1:5760 --out 127.0.0.1:14550 --out 127.0.0.1:14551 --aircraft S500```

Use mavproxy to forward mavlink stream from 5760 to 14550 and 14551. In this case, the ```connection_string``` in the CLI args would be ```udp:127.0.0.1:14551```.

**NOTE:** These streams are UDP only.

## Starting the dev environment
1. Start SIM
2. Start mavproxy.py
3. Connect with scripts

### Starting Thrift server on own laptop
1. python ~/drone/drone-comms/drone/thrift/server.py udp:127.0.0.1:14550 --path /home/adam/drone/drone-comms/drone/thrift/gen-py

### Starting Thrift delivery on laptop 
1. python drone/thrift/delivery.py 14.076550 100.614012 5 --path  /home/adam/drone/drone-comms/drone/thrift/gen-py --drone_id 1

### Starting Thrift farm on laptop
1. python drone/thrift/farm.py "14.3,23.2 12.3,23.2" 5 --path /home/adam/drone/drone-comms/drone/thrift/gen-py --drone_id 3


