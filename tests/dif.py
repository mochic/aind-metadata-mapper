import json
import pathlib

# Two example JSON objects
rig_expected = pathlib.Path(
    "./tests/resources/neuropixels/rig.expected.json"
).read_text()

rig_actual = pathlib.Path(
    "./tests/resources/neuropixels/rig.temp.json"
).read_text()
# Load JSON strings into Python dictionaries
data1 = json.loads(rig_expected)
data2 = json.loads(rig_actual)

# Compare the dictionaries
if data1 == data2:
    print("JSON objects are equal.")
else:
    print("JSON objects are not equal.")

# Find the differences between the two JSON objects
diff = {k: (v, data2[k]) for k, v in data1.items() if v != data2[k]}
print("Differences:", diff)
