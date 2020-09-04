#!/usr/bin/env python3
# encoding=utf-8
# -*- coding: utf-8 -*-

import json
import requests
import xml.etree.ElementTree as ET
import feedparser
import re
from lxml import html
from html.parser import HTMLParser
from subprocess import Popen
import time
import os
from xml.dom import minidom


# working directory
working_dir = '/tmp/wk_images/'
if os.path.isdir(working_dir) == False: os.makedirs(working_dir)

# parse settings file
params_file="settings.xml"
tree = ET.parse(params_file)
root = tree.getroot()

for service in root.findall('service'):
    if service.get('name') == 'station':
        template = service.find('template').text
        subcategory = service.find('subcategory').text
        encoding = service.find('encoding').text
        font = service.find('font').text
        max_title_line_length = int(service.find('max_title_line_length').text)
        max_summary_line_length = int(service.find('max_summary_line_length').text)
        rows = int(service.find('rows').text)
        entry_number = int(service.find('entry_number').text)
        logo = service.find('logo').text
    elif service.get('name') == 'env':
        duration_time = service.find('duration_time').text
        repeat = service.find('repeat').text
        display_reset = service.find('display_reset').text


# parse template file
template_file='template/' + template + '.xml'
tree = ET.parse(template_file)
root = tree.getroot()

for station in root.findall('station'):
    if station.get('name') == subcategory :
        url = station.find('url').text

NewsFeed = feedparser.parse(url)

class WordProccessing:
    def __init__(self, length, rows):
        self.length = length
        self.rows = rows

    def proccessing(self, val):

        words = list()
        for p in re.split(" +", val):
            words += [p]

        row = 0
        row_count = 1
        line = ''
        word_count = len(words)
        for n in words:
            if (len(line) + len(n)) <= self.length and word_count == 1:
                line += n
                word_count = -1
                yield line
            elif (len(line) + len(n) + 1) <= self.length and word_count > 0 and row_count < self.rows:
                line += n + ' '
                word_count -= 1
            elif (len(line) + len(n) + 1) > self.length and word_count > 0 and row_count < self.rows:
                word_count -= 1
                row_count += 1
                yield line
                line = n + ' '
            elif (len(line) + len(n) + 1 - 3) <= self.length and word_count > 0 and row_count == self.rows:
                line += n + ' '
                word_count -= 1
            elif (len(line) + len(n) + 1 - 3) > self.length and word_count > 0 and row_count == self.rows:
                line = line[0:-1] + '...'
                word_count = -1
                yield line


summary = WordProccessing(max_summary_line_length, rows)
title = WordProccessing(max_title_line_length, rows)

def build_source(NewsFeed, title, summary, entry_number, rows):
    data = list()
    news = dict()
    for i in range(0, entry_number):
        news['head'] = NewsFeed.feed['title']
        news['logo'] = logo
        entry = NewsFeed.entries[i]
        for k, v in entry.items():
            if k == 'summary':
                #entry[k] = re.sub(r'"', '\'', entry[k])
                entry[k] = entry[k].replace("\"", "\'")
                entry[k] = entry[k].replace(u"\u2019", "\'")
                news['summary'] = summary.proccessing(entry[k])
            elif k == 'title':
                #entry[k] = re.sub(r'"', '\'', entry[k])
                entry[k] = entry[k].replace("\"", "\'")
                entry[k] = entry[k].replace(u"\u2019", "\'")
                news['title'] = title.proccessing(entry[k])
            elif k == 'published':
                news['published'] = entry[k]
            elif k == 'link':
                page = requests.get(entry[k])
                tree = html.fromstring(page.content)

                for m in tree.xpath('//meta[@property="og:image"]'):
                    img_url = m.get("content")
                    file1 = working_dir + 'image' + str(i)
                    file2 = working_dir + 'image' + str(i) + '.bmp'
                    file3 = working_dir + 'image' + str(i) + '.svg'
                    file4 = working_dir + 'image' + str(i) + '.png'
                    args1 = ['wget', '-q', img_url, '-O', file1]
                    args2 = ['convert', '-enhance', '-equalize', '-contrast', '-resize', '600x', file1, file2]
                    args3 = ['potrace', '--svg', file2, '-o', file3]
                    args4 = ['convert',  '-size', '600x', '-background', 'white', '-depth', '8' ,file3, file4]

                    output = Popen(args1)
                    time.sleep(3)
                    output = Popen(args2)
                    time.sleep(3)
                    output = Popen(args3)
                    time.sleep(3)
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
encoding = 'iso-8859-1'
font = 'Droid Sans'
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

    svg_file.write('<line x1="10" x2="590" y1="45" y2="45" style="fill:none;stroke:black;stroke-width:1px;"/>' + '\n')

    # title
    n = 100
    for p in news['title']:
        svg_file.write('<text style="text-anchor:start;" font-size="40px" x="20" y="' + str(n) + '">')
        svg_file.write(p)
        svg_file.write('</text>\n')
        n += 50

    # published
    n = 275
    svg_file.write('<text style="text-anchor:start;" font-weight="bold" font-size="30px" x="20" y="' + str(n) + '">')
    svg_file.write(news['published'])
    svg_file.write('</text>\n')

    # summary
    n = 350
    for p in news['summary']:
        svg_file.write('<text style="text-anchor:start;" font-size="30px" x="25" y="' + str(n) + '">')
        svg_file.write(p)
        svg_file.write('</text>\n')
        n += 40

    svg_file.write('</g>\n')
    # image
    svg_file.write('<g transform="translate(0.000000,800.000000) scale(0.100000,-0.100000)" fill="#000000" stroke="none">\n')
    for p in news['img']:
        svg_file.write('<path d="' + p + '"/>\n')

    svg_file.write('</g>\n')
    svg_file.write('</svg>')
    svg_file.close()


news_data = build_source(NewsFeed, title, summary, entry_number, rows)

# image processing

# working directory
working_dir2 = '/tmp/wk_images/output/'
if os.path.isdir(working_dir2) == False: os.makedirs(working_dir2)

i = 0
for news in news_data:
    filename = working_dir + 'entry' + str(i) + '.svg'
    output_file = working_dir2 + 'entry' + str(i) + '.png'
    create_svg(news, filename)

    args = ['convert', '-size', '600x800',  '-background', 'white', '-depth', '8', filename, output_file]
    output = Popen(args)
    i += 1

# create control file
control_file = working_dir2 + 'control.env'

svg_file = open(control_file, "w")

svg_file.write('duration_time=' + duration_time + '\n')
svg_file.write('repeat=' + repeat + '\n')
svg_file.write('display_reset="' + display_reset + '"\n')
svg_file.close()
