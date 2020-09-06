#!/bin/sh

cd "$(dirname "$0")"

pidof powerd >/dev/null
if [ $? -eq 0 ]; then
    /etc/init.d/powerd stop
    /etc/init.d/framework stop
fi

rm -f /tmp/news_feeds.tar
wget -q http://192.168.2.1:8080/news_feeds.tar -O /tmp/news_feeds.tar

[ -d /tmp/news-feeds ] || mkdir -p /tmp/news-feeds
[ -f /tmp/news-feeds/control.env ] && rm /tmp/news-feeds/*

tar xf /tmp/news_feeds.tar -C /tmp/news-feeds

. /tmp/news-feeds/control.env

run()
{
    count=0
    while [ $count -lt $repeat ]; do
        count=`expr $count + 1`
        for n in `echo /tmp/news-feeds/entry*.png`; do
            eips -g $n
            sleep $duration_time
            if [ $display_reset = 'True' ]; then
                eips -c
            elif [ $display_reset = 'False' ]; then
                continue
            fi
        done
    done
}

eips -c
if [ -f '/tmp/news-feeds/entry0.pngz' ]; then
    run
else
    eips -g error.png
fi

