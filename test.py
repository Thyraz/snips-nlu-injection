#!/usr/bin/env python3
import json
import re

# Read original intent file
with open('intent_parser.json', encoding='utf-8') as data_file:
    intentData = json.loads(data_file.read())
    nameToSlotDict =  intentData['group_names_to_slot_names']
    slotToEntityDict = intentData['slot_names_to_entities']
    samplesDict = intentData['patterns']

# Parse JSON from MQTT and create a dictionary with entitiy -> value-array entries
injectDict = {}
injectData = json.loads('{"operations": [["add",{"de.fhem.Device": ["Bogenlampe","Deckenlampe","Waschanlage","Schreibtischlampe","Thermometer"]}],["add", {"de.fhem.Room": ["Wohnzimmer", "Wintergarten"]}]]}')
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

# Write new JSON data to file
with open('dump.json', 'w', encoding='utf-8') as outfile:
    json.dump(intentData, outfile, sort_keys=True, indent=2)
