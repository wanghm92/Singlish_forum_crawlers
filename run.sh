#!/bin/bash

BLOG=$1
END=$3
INCREMENT=$2

for i in $(seq 1 $INCREMENT $END)
do
    echo 'Crawling from page '$i
    touch $BLOG-$i.log
    ls $BLOG-$i.log
    nohup time -p python craw_market.py -g $i -r $INCREMENT 1>$BLOG-$i.log 2>&1 &

done