#!/bin/bash

mkdir -p log/hardwarezone
mkdir -p outputs/hardwarezone

for i in $(seq 0 1 27)
do
    echo 'Crawling BATCH '$i

    touch log/hardwarezone/hardwarezone-crawl-batch$i.log
    ls log/hardwarezone/hardwarezone-crawl-batch$i.log
    nohup time -p python craw_hardwarezone_craw.py -b $i 1>log/hardwarezone/hardwarezone-crawl-batch$i.log 2>&1 &
done