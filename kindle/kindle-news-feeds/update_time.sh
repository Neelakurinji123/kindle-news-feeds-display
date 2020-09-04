#!/bin/sh

DEBIAN_PATH=/mnt/us/DebianKindle/mnt

chroot $DEBIAN_PATH /bin/bash -c "ntpdate 192.168.2.1 >/dev/null 2>&1"
