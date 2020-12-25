#!/bin/sh

cd "$(dirname "$0")"

if [ -f /mnt/us/kindle-weather/enable ]; then

    if [ "`pidof powerd`" != '' ]; then
        /etc/init.d/powerd stop
        /etc/init.d/framework stop
    fi

    if [ "`mount -l | grep 'tmpfs on /www'`" == '' ]; then
        mount -a
        sleep 3
    fi

    rm -f /www/news_feeds.tar
    wget -q http://192.168.2.1:8080/news_feeds.tar -O /www/news_feeds.tar

    [ -d /www/news-feeds ] || mkdir -p /www/news-feeds
    [ -f /www/news-feeds/control.env ] && rm -rf /www/news-feeds/*

    tar xf /www/news_feeds.tar -C /www/news-feeds

    . /www/news-feeds/control.env

    run()
    {
        count=0
        while [ $count -lt $repeat ]; do
            count=`expr $count + 1`
            for n in `echo /www/news-feeds/entry*.png`; do
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

    if [ -f '/www/news-feeds/entry0.png' ]; then
        run
    else
        eips -g error.png
    fi
fi

