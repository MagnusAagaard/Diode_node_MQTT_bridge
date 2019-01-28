# mqtt_bridge

mqtt_bridge provides a functionality to bridge between ROS and MQTT in bidirectional.
The bridge was not developed by me, only modified for personal use.
All credit goes to: https://github.com/groove-x/mqtt_bridge

# Diode_node
Used to control diodes through ROS topics and MQTT.

## Setup
Install mosquitto: ```$ sudo apt-get install mosquitto mosquitto-clients```

Install other requirements: ```$ pip install -r requirements.txt```

Make Python scripts executable - Navigate to /mqtt_bridge/scripts and type ```$ chmod +x mqtt_bridge_node.py``` and ```$ chmod +x mqtt_server_node.py``` (the latter is not really required, it's part of another project).

Install pymongo for BSON: ```$ pip install pymongo```

Might need: ```$ sudo apt-get install ros-$distro-rosbridge-suite```

### Config file
Change the config file /mqtt_bridge/config/diode_launcher_params.yaml to define bridges between MQTT and ROS and to define the host.

### Running
To run the diode_node use: ```$ roslaunch diode_node diode_node_launcher.launch```

## License

This software is released under the MIT License, see LICENSE.txt.
