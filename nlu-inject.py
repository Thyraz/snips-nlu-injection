#!/usr/bin/env python3
import json
import os
import string
import re
import subprocess
from pathlib import Path
from pprint import pprint

import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import toml

def on_connect(client, userdata, flags, rc):
    print("MQTT connected")
    client.subscribe("hermes/asr/inject")


# Received message from MQTT
def update_nlu(client, userdata, msg):
    # Read original intent file
    with open('/usr/share/snips/assistant/nlu_engine/deterministic_intent_parser/intent_parser.json', encoding='utf-8') as data_file:
        intentData = json.loads(data_file.read())
        nameToSlotDict =  intentData['group_names_to_slot_names']
        slotToEntityDict = intentData['slot_names_to_entities']
        samplesDict = intentData['patterns']

    # Parse JSON from MQTT and create a dictionary with entitiy -> value-array entries
    injectDict = {}
    injectData = json.loads(msg.payload.decode())
    operations = injectData['operations']
    for operation in operations:
        if len(operation) >= 2 and operation[0].lower() == 'add':
            injectDict.update(operation[1])

    # Loop over samples -> extract slot-groups -> get matching entities -> inject new words
    regex = r"<(.+?)>+?"
    for (intent, samples) in samplesDict.items():
        for (i, sample) in enumerate(samples):
            slotGroups = re.findall(regex, sample)

            for slotGroup in slotGroups:
                slotName = nameToSlotDict[slotGroup]
                entity = slotToEntityDict[intent][slotName]

                if entity in injectDict:
                    startIndex = sample.find('<' + slotGroup + '>') + len(slotGroup) + 2

                    for slotValue in injectDict[entity]:
                        if sample.find(slotValue.lower()) == -1:
                            sample = sample[:startIndex] + slotValue.lower() + "|" + sample[startIndex:]

            samples[i] = sample

            # bak File erstellen?
            # Datei überschreiben statt neuer Name
            # NLU Service neu starten?

    # Write new JSON data to file
    with open('/home/tobias/dump.json', 'w', encoding='utf-8') as outfile:
        json.dump(intentData, outfile, sort_keys=True, indent=2)



# Read MQTT connection info from the central snips config.
snips_config = toml.loads(open("/etc/snips.toml").read())

client = mqtt.Client()
client.on_connect = on_connect

client.message_callback_add("hermes/asr/inject", update_nlu)

mqtt_host, mqtt_port = snips_config["snips-common"]["mqtt"].split(":")
mqtt_port = int(mqtt_port)
client.connect(mqtt_host, mqtt_port, 60)

client.loop_forever()
