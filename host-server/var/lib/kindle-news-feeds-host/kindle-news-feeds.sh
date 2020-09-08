#!/bin/sh

OUTPUT_DIR=/tmp/www
WORKING_DIR=/tmp/wk_images/output

test -d /tmp/www || mkdir -p /tmp/www
test -f /tmp/wk_images/image0 && rm /tmp/wk_images/image*
test -d /tmp/wk_images/output && rm /tmp/wk_images/output/*

cd "$(dirname "$0")"

/usr/bin/python3 createSVG.py $1
sleep 5
(cd $WORKING_DIR; for n in `echo entry*.png`; do pngcrush -s -c 0 -ow $n; done)
(cd $WORKING_DIR; tar cf $OUTPUT_DIR/news_feeds.tar *)
