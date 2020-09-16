#!/usr/bin/env python3
# encoding=utf-8
# -*- coding: utf-8 -*-

import json
import os
import sys
import requests
import xml.etree.ElementTree as ET

outfile = '/tmp/daytime.dat'
tree = ET.parse('display.xml')
root = tree.getroot()

def renewDaytime(root, outfile):
    for service in root.findall('service'):
        lat = service.find('lat').text
        lng = service.find('lng').text
        url = service.find('url').text + 'lat=' + lat + '&lng=' + lng + '&formatted=0'

    d = requests.get(url).json()
    with open(outfile, 'w') as outfile:
        json.dump(d, outfile)

def jsonfile():
    renewDaytime(root, outfile)
