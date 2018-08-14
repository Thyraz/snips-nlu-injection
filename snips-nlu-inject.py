#!/usr/bin/env python3
import json
import os
import string
import subprocess
from pathlib import Path

import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import toml

def on_connect(client, userdata, flags, rc):
    print("MQTT connected")
    client.subscribe("hermes/asr/inject")


def update_nlu(client, userdata, msg):
    data = json.loads(msg.payload.decode())
    pprint(data)


# https://stackoverflow.com/questions/8369219/how-do-i-read-a-text-file-into-a-string-variable-in-python
# https://stackoverflow.com/questions/16720541/python-string-replace-regular-expression

# Read MQTT connection info from the central snips config.
snips_config = toml.loads(open("/etc/snips.toml").read())

client = mqtt.Client()
client.on_connect = on_connect

client.message_callback_add("hermes/asr/inject", update_nlu)

mqtt_host, mqtt_port = snips_config["snips-common"]["mqtt"].split(":")
mqtt_port = int(mqtt_port)
client.connect(mqtt_host, mqtt_port, 60)

client.loop_forever()
