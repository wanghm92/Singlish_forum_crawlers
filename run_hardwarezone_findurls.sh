#!/bin/bash

mkdir -p log/hardwarezone
mkdir -p outputs/hardwarezone

for i in $(seq 0 1 27)
do
    echo 'Crawling BATCH '$i

    touch log/hardwarezone/hardwarezone-moreurl-batch$i.log
    ls log/hardwarezone/hardwarezone-moreurl-batch$i.log
    touch outputs/hardwarezone/more_target_urls.hdz.txt
    touch outputs/hardwarezone/global_reply_estimate.txt
    nohup time -p python craw_hardwarezone_findmore_urls.py -b $i -s 5 1>log/hardwarezone/hardwarezone-moreurl-batch$i.log 2>&1 &
done