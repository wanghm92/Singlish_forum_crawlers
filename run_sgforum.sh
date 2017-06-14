#!/bin/bash

for i in $(seq 0 1 12)
do
    echo 'Crawling BATCH '$i
    touch log/sgforum/sgforum-batch$i.log
    ls log/sgforum/sgforum-batch$i.log
    nohup time -p python craw_sgforum_craw.py -b $i 1>log/sgforum/sgforum-batch$i.log 2>&1 &
done