#!/bin/bash

source marionette-env/bin/activate

# this is suitable for an 2 core machine
INDEX=0
for i in `seq 8`; do
  for x in `seq 2`; do
    ./run_slimtest.py --binary firefox/firefox-bin --sqlitedb db/custom-erahm-variance.sqlite --buildname $INDEX --buildtime $INDEX --batchnum $x &
    INDEX=$(($INDEX + 1))
    sleep 1
  done
  wait
done
