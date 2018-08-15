#!/usr/bin/env python3
import json
import re

# Read original intent file
with open('intent_parser.json', encoding='utf-8') as data_file:
    intentData = json.loads(data_file.read())
    nameToSlotDict =  intentData['group_names_to_slot_names']
    slotToEntityDict = intentData['slot_names_to_entities']
    samplesDict = intentData['patterns']

# Parse JSON from MQTT
injectData = json.loads('{"operations": [["add",{"de.fhem.Device": ["Bogenlampe","Deckenlampe","Waschanlage","Schreibtischlampe","Thermometer"]}],["add", {"de.fhem.Room": ["Wohnzimmer", "Wintergarten"]}]]}')
operations = injectData['operations']


# Loop over samples -> extract slot-groups -> get matching entities -> inject new words
regex = r"<(.+?)>+?"
for (intent, samples) in samplesDict.items():
    for sample in samples:
        slotGroups = re.findall(regex, sample)
        print(slotGroups)



# # Loop over single add opperations
# for operation in operations:
#     if len(operation) >= 2 and operation[0].lower() == 'add':
#         operationData = operation[1]
#
#         for (entitiy, values) in operationData.items():
#             # slot_names_to_entities durchlaufen, immer suchen ob dort die entity verwendet wird und unter welchem slot_names_to_entities
#             # Dann



# Write new JSON data to file
with open('dump.json', 'w', encoding='utf-8') as outfile:
    json.dump(intentData, outfile, sort_keys=True, indent=2)
