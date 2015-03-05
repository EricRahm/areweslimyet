#!/bin/env python

import gzip
import json


with gzip.open('arcus-areweslimyet-2015-03.json.gz') as f:
    arcus_data = json.load(f)

with gzip.open('awsy1-areweslimyet-2015-03.json.gz') as f:
    awsy1_data = json.load(f)

explicit_data_points = [
    "StartMemoryV2",
    "StartMemorySettledV2",
    "MaxMemoryV2",
    "MaxMemorySettledV2",
    "MaxMemoryForceGCV2",
    "EndMemoryV2",
    "EndMemorySettledV2",
    "EndMemoryForceGCV2"
]

explicit_data_points = [ "EndMemorySettledV2" ]
print "revision,EndMemorySettled - arcus, EndMemorySettled - awsy1"

#print ','.join([ 'revision'] + explicit_data_points)

arcus = dict()
for build in arcus_data['builds']:
   arcus[build['revision']] = build['test_ids'][1]

for build in awsy1_data['builds']:
    rev = build['revision']
    test_id = build['test_ids'][1]
    if not test_id or not rev in arcus:
        continue

    row = [ rev ]
    for data_point in explicit_data_points:
        awsy_val = awsy1_data["series"][data_point][int(test_id) - 1]
        arcus_val = arcus_data["series"][data_point][arcus[rev] - 1]
        if awsy_val:
            row.append(str(arcus_val))
            row.append(str(awsy_val))
            #delta = (arcus_val - awsy_val) / float(arcus_val) 
            #row.append("%.4f" % delta)
        else:
            row.append("None,None")

    print ','.join(row)
