# drone-comms
A testbed for drone-server communications

## Starting the simulator
### Dronekit
home location - 14.079140, 100.609484

Run ```dronekit-sitl copter --home=14.079140,100.609484,584,353```

This runs the SITL sim on port 5760 with the specified home location(lat,lng,alt,yaw).

### Ardupilot
TODO


## Scripts

### hello-drone

**(IMPORTANT)** Requirements: Python 2.7

Pip packages: dronekit, dronekit-sitl(optional)

Run ```python hello-drone.py --connection_string--``` to get a basic status message.

The ```connection_string``` can be USB, serial or network.

For example: ```python hello-drone.py tcp:127.0.0.1:5760``` will connect to a SITL simulator running at port TCP 5760 on the local machine.



