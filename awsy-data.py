#!/bin/env python

import gzip
import json


with gzip.open('html/data/erahm-variance.json.gz') as f:
    arcus_data = json.load(f)

#with gzip.open('awsy1-areweslimyet-2015-03.json.gz') as f:
#    awsy1_data = json.load(f)

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

#explicit_data_points = [ "EndMemorySettledV2" ]
#print "revision,EndMemorySettled - arcus, EndMemorySettled - awsy1"

print ','.join("%12s" % point for point in [ 'revision' ] + explicit_data_points)

arcus = dict()
for build in arcus_data['builds']:
   arcus[build['revision']] = build['test_ids'][1]

build_results = [ ]
for build in arcus_data['builds']:
    rev = build['revision'][:12]
    test_id = build['test_ids'][1]
    if not test_id or not rev in arcus:
        continue

    row = [ ]
    for data_point in explicit_data_points:
        arcus_val = arcus_data["series"][data_point][int(test_id) - 1]
        #arcus_val = arcus_data["series"][data_point][arcus[rev] - 1]
        if arcus_val:
            #row.append(str(arcus_val))
            #row.append(str(awsy_val))
            #delta = (arcus_val - awsy_val) / float(arcus_val) 
            row.append(arcus_val)
        else:
            break
    if not row:
      continue

    build_results.append(row)
    print ','.join([ "%12s" % rev ] + [ "%12d" % (val / 1024) for val in row ])

import numpy as np
a = np.array(build_results)
stddev = a.std(axis=0)
mean = a.mean(axis=0)

print ','.join([ '%12s' % 'mean' ] + [ "%12d" % (val / 1024) for val in mean ])
print ','.join([ '%12s' % 'stddev' ] + [ "%12.3f" % (val / 1024) for val in stddev ])
