#!/usr/bin/env python3
# encoding=utf-8
# -*- coding: utf-8 -*-

import json
import time as t
import os
import sys
import re
import requests
import feedparser
import xml.etree.ElementTree as ET
from subprocess import Popen
from lxml import html
from html.parser import HTMLParser
from xml.dom import minidom
import fontconfig
from PIL import ImageFont
from datetime import datetime, date
import pytz
import astral

# working directory
working_dir = '/tmp/wk_images/'
if os.path.isdir(working_dir) == False: os.makedirs(working_dir)

# parse settings file

# if using custom settings.xml, add a setting file on the commandline.
if len(sys.argv) > 1:
    params_file = sys.argv[1]
else:
    params_file = "settings.xml"

tree = ET.parse(params_file)
root = tree.getroot()

for service in root.findall('service'):
    if service.get('name') == 'station':
        template = service.find('template').text
        category = service.find('category').text
        encoding = service.find('encoding').text
        font = service.find('font').text
        title_font_size = int(service.find('title_font_size').text)
        summary_font_size = int(service.find('summary_font_size').text)
        title_rows = int(service.find('title_rows').text)
        summary_rows = int(service.find('summary_rows').text)
        entry_number = int(service.find('entry_number').text)
        logo = service.find('logo').text
    elif service.get('name') == 'env':
        duration_time = service.find('duration_time').text
        repeat = service.find('repeat').text
        display_reset = service.find('display_reset').text

# font path
fonts = fontconfig.query(family=font,lang='en')
for i in range(0, len(fonts)):
    if fonts[i].style[0][1] == 'Regular':
        font_path = fonts[i].file

# parse template file
template_file='template/' + template + '.xml'
tree = ET.parse(template_file)
root = tree.getroot()

for station in root.findall('station'):
    if station.get('name') == category :
        url = station.find('url').text

# image path
image = root.find('image')
img_path = image.find('img_path').text

NewsFeed = feedparser.parse(url)


# dark mode
tree = ET.parse('display.xml')
root = tree.getroot()
for service in root.findall('service'):
    if service.get('name') == 'display':
        dark_mode = service.find('dark_mode').text
        lat = float(service.find('lat').text)
        lng = float(service.find('lng').text)
        t_timezone = service.find('timezone').text
        offset = int(datetime.now(pytz.timezone(t_timezone)).strftime('%z')) / 100
        if dark_mode == 'Auto':
            t_now = int(datetime.now().timestamp())
            loc = astral.Location(('', '', lat, lng, 'GMT+0'))
            for event, time in loc.sun(date.today()).items():
                if event == 'sunrise':
                    t_sunrise = int(datetime.timestamp(time))
                elif event == 'sunset':
                    t_sunset = int(datetime.timestamp(time))

            t_now = (t_now + offset * 3600) % 86400
            t_sunrise = (t_sunrise + offset * 3600) % 86400
            t_sunset = (t_sunset + offset * 3600) % 86400
            if t_sunrise > t_now or t_sunset < t_now:
                dark_mode = 'True'
            else:
                dark_mode = 'False'


class WordProccessing:
    def __init__(self, length, rows, f_path, f_size):
        self.length = int(length)
        self.rows = int(rows)
        self.font = ImageFont.truetype(f_path, f_size)

    def proccessing(self, val):
        words = list()

        # remove a garbage
        val = re.sub('<.*$', '', val)

        for s in re.split(" +", val):
            words += [s]

        row = 0
        row_counter = 1
        line = str()
        # = len(words)

        for i, s in enumerate(words, 1):
            if self.font.getsize(line + s)[0] <= self.length and len(words) == i:
                line += s
                yield line
            elif self.font.getsize(line + s)[0] <= self.length and len(words) > i and row_counter < self.rows:
                line += s + ' '
            elif self.font.getsize(line + s)[0] > self.length and len(words) > i and row_counter < self.rows:
                row_counter += 1
                yield line[0:-1]
                line = s + ' '
            elif self.font.getsize(line + s)[0] > self.length and len(words) == i and row_counter < self.rows:
                yield line[0:-1]
                yield s
            elif ((self.font.getsize(line + s)[0] + self.font.getsize('...')[0]) <= self.length and
                      len(words) > i and row_counter == self.rows):
                line += s + ' '
            elif (self.font.getsize(line + s)[0] <= self.length and
                     (self.font.getsize(line + s)[0] + self.font.getsize('...')[0]) > self.length and
                     len(words) > i and row_counter == self.rows):
                line = line[0:-1] + '...'
                yield line
                break
            elif (self.font.getsize(line + s)[0] <= self.length and
                     len(words) == i and row_counter == self.rows):
                line += s
                yield line
                break
            elif (self.font.getsize(line + s)[0] > self.length and
                     len(words) == i and row_counter == self.rows):
                line = line[0:-1] + '...'
                yield line
                break

n = 550
summary = WordProccessing(n, summary_rows, font_path, summary_font_size)
title = WordProccessing(n, title_rows, font_path, title_font_size)

def build_source(NewsFeed, title, summary, entry_number):
    data = list()
    news = dict()
    for i in range(0, entry_number):
        news['head'] = NewsFeed.feed['title']
        news['logo'] = logo
        entry = NewsFeed.entries[i]
        for k, v in entry.items():
            if k == 'summary':

                # hmm, tricky problem...
                entry[k] = entry[k].replace("\"", "\'\'")
                entry[k] = entry[k].replace(u"\u2018", "\'")
                entry[k] = entry[k].replace(u"\u2019", "\'")
                news['summary'] = summary.proccessing(entry[k])
            elif k == 'title':
                entry[k] = entry[k].replace("\"", "\'\'")
                entry[k] = entry[k].replace(u"\u2018", "\'")
                entry[k] = entry[k].replace(u"\u2019", "\'")
                news['title'] = title.proccessing(entry[k])
            elif k == 'published':
                news['published'] = entry[k]
            elif k == 'link':
                page = requests.get(entry[k])
                tree = html.fromstring(page.content)

                for m in tree.xpath(img_path):
                    img_url = m.get("content")
                    file1 = working_dir + 'image' + str(i)
                    file2 = working_dir + 'image' + str(i) + '.bmp'
                    file3 = working_dir + 'image' + str(i) + '.svg'
                    file4 = working_dir + 'image' + str(i) + '.png'
                    args1 = ['wget', '-q', img_url, '-O', file1]
                    args2 = ['convert', '-enhance', '-equalize', '-contrast', '-resize', '600x', file1, file2]

                    if dark_mode == 'True':
                        args3 = ['potrace', '-i', '--svg', file2, '-o', file3]
                    else:
                        args3 = ['potrace', '--svg', file2, '-o', file3]

                    args4 = ['gm', 'convert',  '-size', '600x', '-background', 'white', '-depth', '8' ,file3, file4]

                    output = Popen(args1)
                    t.sleep(5)
                    output = Popen(args2)
                    t.sleep(5)
                    output = Popen(args3)
                    t.sleep(5)
                    output = Popen(args4)

                    doc = minidom.parse(file3)
                    svg_path = [path.getAttribute('d') for path
                                in doc.getElementsByTagName('path')]
                    doc.unlink()
                    news['img'] = svg_path

        data += [news]
        news = dict()

    return data


# Create SVG file
def create_svg(news, filename):

    svg_file = open(filename,"w", encoding=encoding)
    svg_file.write('<?xml version="1.0" encoding="' + encoding + '"?>\n')
    svg_file.write('<svg xmlns="http://www.w3.org/2000/svg" height="800" width="600" version="1.1" xmlns:xlink="http://www.w3.org/1999/xlink">\n')
    svg_file.write('<g font-family="' + font + '">\n')

    # Parsing values
    # head
    svg_file.write('<text style="text-anchor:start;" font-size="30px" x="20" y="38">')
    svg_file.write(news['head'].replace('&', 'and'))
    svg_file.write('</text>\n')

    # logo
    #svg_file.write('<text style="text-anchor:end;" font-size="30px" x="580" y="40">')
    #svg_file.write("%s" % (maintenant))
    #svg_file.write('</text>\n')

    # line
    svg_file.write('<line x1="10" x2="590" y1="45" y2="45" style="fill:none;stroke:black;stroke-width:1px;"/>' + '\n')

    # title
    n = 210
    for s in reversed(list(news['title'])):
        svg_file.write('<text style="text-anchor:start;" font-size="' + str(title_font_size) + 'px" x="20" y="' + str(n) + '">')

        # fix graphics processing bug
        s = re.sub('^\'', '\'\'', s)
        s = re.sub('\'$', '\'\'', s)
        if s != '': svg_file.write(s)
        svg_file.write('</text>\n')
        n -= 50

    # published
    n = 275 if summary_rows == 3 else 260
    svg_file.write('<text style="text-anchor:start;" font-weight="bold" font-size="30px" x="20" y="' + str(n) + '">')
    svg_file.write(news['published'])
    svg_file.write('</text>\n')

    # summary
    n = 340 if summary_rows == 3 else 310
    for s in news['summary']:
        svg_file.write('<text style="text-anchor:start;" font-size="' + str(summary_font_size) + 'px" x="25" y="' + str(n) + '">')

        # fix graphics processing bug
        s = re.sub('^\'', '\'\'', s)
        s = re.sub('\'$', '\'\'', s)
        svg_file.write(s)
        svg_file.write('</text>\n')
        n += 40

    svg_file.write('</g>\n')
    # image
    svg_file.write('<g transform="translate(0.000000,800.000000) scale(0.100000,-0.100000)" fill="#000000" stroke="none">\n')
    for s in news['img']:
        svg_file.write('<path d="' + s + '"/>\n')

    svg_file.write('</g>\n')
    svg_file.write('</svg>')
    svg_file.close()

news_data = build_source(NewsFeed, title, summary, entry_number)


# image processing

# working directory
working_dir2 = '/tmp/wk_images/output/'
if os.path.isdir(working_dir2) == False: os.makedirs(working_dir2)

i = 0
for news in news_data:
    filename = working_dir + 'entry' + str(i) + '.svg'
    output_file = working_dir2 + 'entry' + str(i) + '.png'
    create_svg(news, filename)

    if dark_mode == 'True':
        #args = ['convert', '-size', '600x800',  '-background', 'white', '-depth', '8', '-negate', filename, output_file]
        args = ['gm', 'convert', '-size', '600x800', '-background', 'white', '-depth', '8', '-resize', '600x800', '-colorspace', 'gray', '-type', 'palette', '-geometry', '600x800', '-negate', filename, output_file]
        output = Popen(args)
    else:
        #args = ['convert', '-size', '600x800',  '-background', 'white', '-depth', '8', filename, output_file]
        args = ['gm', 'convert', '-size', '600x800', '-background', 'white', '-depth', '8', '-resize', '600x800', '-colorspace', 'gray', '-type', 'palette', '-geometry', '600x800', filename, output_file]
        output = Popen(args)

    i += 1


# create control file
control_file = working_dir2 + 'control.env'

svg_file = open(control_file, "w")

svg_file.write('duration_time=' + duration_time + '\n')
svg_file.write('repeat=' + repeat + '\n')
svg_file.write('display_reset="' + display_reset + '"\n')
svg_file.close()
