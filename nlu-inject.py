#!/usr/bin/env python3
import json
import os
import string
import re
import dbus
from pathlib import Path

import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import toml


# Subscribe inject topics
def on_connect(client, userdata, flags, rc):
    print("MQTT connected")
    client.subscribe("hermes/asr/inject")

# Received message from MQTT
def update_nlu(client, userdata, msg):
    # Parse JSON from MQTT and create a dictionary with entitiy -> value-array entries
    injectDict = {}
    injectData = json.loads(msg.payload.decode())
    operations = injectData['operations']
    for operation in operations:
        if len(operation) >= 2 and operation[0].lower() == 'add':
            injectDict.update(operation[1])

    # Patch intent_parser.json
    with open('/usr/share/snips/assistant/nlu_engine/deterministic_intent_parser/intent_parser.json', encoding='utf-8') as intent_file:
        intentData = json.loads(intent_file.read())
        nameToSlotDict =  intentData['group_names_to_slot_names']
        slotToEntityDict = intentData['slot_names_to_entities']
        samplesDict = intentData['patterns']

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

        # Write new JSON data to file
        with open('/usr/share/snips/assistant/nlu_engine/deterministic_intent_parser/intent_parser.json', 'w', encoding='utf-8') as outfile:
            json.dump(intentData, outfile, sort_keys=True, indent=2)

    # Patch nlu_engine.json
    with open('/usr/share/snips/assistant/nlu_engine/nlu_engine.json', encoding='utf-8') as nlu_file:
        nluData = json.loads(nlu_file.read())
        entities = nluData['dataset_metadata']['entities']

        for (entity,entityData) in entities.items():
            if entity in injectDict:
                utterances = entityData['utterances']
                injectValues = injectDict[entity]

                for injectValue in injectValues:
                    utterances[injectValue] = injectValue
                    utterances[injectValue.lower()] = injectValue

        with open('/usr/share/snips/assistant/nlu_engine/nlu_engine.json', 'w', encoding='utf-8') as outfile:
            json.dump(nluData, outfile, sort_keys=True, indent=2)

    # Restart nlu service
    sysbus = dbus.SystemBus()
    systemd1 = sysbus.get_object('org.freedesktop.systemd1', '/org/freedesktop/systemd1')
    manager = dbus.Interface(systemd1, 'org.freedesktop.systemd1.Manager')
    job = manager.RestartUnit('snips-nlu.service', 'fail')


# Read MQTT connection info from the central snips config.
snips_config = toml.loads(open("/etc/snips.toml").read())

# Create client and callback
client = mqtt.Client()
client.on_connect = on_connect
client.message_callback_add("hermes/asr/inject", update_nlu)

mqtt_host, mqtt_port = snips_config["snips-common"]["mqtt"].split(":")
mqtt_port = int(mqtt_port)
client.connect(mqtt_host, mqtt_port, 60)

client.loop_forever()
