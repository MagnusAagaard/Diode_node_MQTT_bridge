#!/usr/bin/env python
# -*- coding: utf-8 -*-
import rospy

from mqtt_bridge.MQTT_GUI import mqtt_server_node


try:
    mqtt_server_node()
except rospy.ROSInterruptException:
    pass
