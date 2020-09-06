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
from PIL import ImageFont
import fontconfig

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
        title_font_size = service.find('title_font_size').text
        summary_font_size = service.find('summary_font_size').text
        rows = service.find('rows').text
        entry_number = service.find('entry_number').text
        logo = service.find('logo').text
    elif service.get('name') == 'env':
        duration_time = service.find('duration_time').text
        repeat = service.find('repeat').text
        display_reset = service.find('display_reset').text

# font path
fonts = fontconfig.query(family=font,lang='en')
for i in range(0, len(fonts)):
    if fonts[i].style[0][1] == 'Regular':
        f_path = fonts[i].file


# parse template file
template_file='template/' + template + '.xml'
tree = ET.parse(template_file)
root = tree.getroot()

for station in root.findall('station'):
    if station.get('name') == subcategory :
        url = station.find('url').text

NewsFeed = feedparser.parse(url)

class WordProccessing:
    def __init__(self, length, rows, f_path, f_size):
        self.length = int(length)
        self.rows = int(rows)
        self.font = ImageFont.truetype(f_path, int(f_size))

    def proccessing(self, val):
        words = list()
        for s in re.split(" +", val):
            words += [s]

        row = 0
        row_count = 1
        line = str()
        word_count = len(words)

        for s in words:
            if self.font.getsize(line + s)[0] <= self.length and word_count == 1:
                line += s
                word_count = 0
                yield line
            elif self.font.getsize(line + s)[0] <= self.length and word_count > 1 and row_count <= self.rows:
                line += s + ' '
                word_count -= 1
            elif self.font.getsize(line + s)[0] > self.length and word_count > 1 and row_count <= self.rows:
                word_count -= 1
                row_count += 1
                yield line[0:-1]
                line = s + ' '
            elif (self.font.getsize(line + s)[0] - self.font.getsize('...')[0]) <= self.length and word_count > 1 and row_count == self.rows:
                line += s + ' '
                word_count -= 1
            elif (self.font.getsize(line + s)[0] - self.font.getsize('...')[0]) > self.length and word_count > 1 and row_count == self.rows:
                line = line[0:-1] + '...'
                word_count = 0
                yield line
            # something wrong with the logic
            else:
                yield line
                line = str()

n = 550
summary = WordProccessing(n, rows, f_path, summary_font_size)
title = WordProccessing(n, rows, f_path, title_font_size)

def build_source(NewsFeed, title, summary, entry_number):
    data = list()
    news = dict()
    for i in range(0, int(entry_number)):
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
                    time.sleep(5)
                    output = Popen(args2)
                    time.sleep(5)
                    output = Popen(args3)
                    time.sleep(5)
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
        svg_file.write('<text style="text-anchor:start;" font-size="' + title_font_size + 'px" x="20" y="' + str(n) + '">')

        # fix graphics processing bug
        s = re.sub('^\'', '\'\'', s)
        s = re.sub('\'$', '\'\'', s)
        if s != '': svg_file.write(s)
        svg_file.write('</text>\n')
        n -= 50

    # published
    n = 275
    svg_file.write('<text style="text-anchor:start;" font-weight="bold" font-size="30px" x="20" y="' + str(n) + '">')
    svg_file.write(news['published'])
    svg_file.write('</text>\n')

    # summary
    n = 340
    for s in news['summary']:
        svg_file.write('<text style="text-anchor:start;" font-size="' + summary_font_size + 'px" x="25" y="' + str(n) + '">')

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

    #args = ['convert', '-size', '600x800',  '-background', 'white', '-depth', '8', filename, output_file]
    args = ['gm', 'convert', '-size', '600x800', '-background', 'white', '-depth', '8', '-resize', '600x800', '-colorspace', 'gray', '-type', 'palette', '-geometry', '600x800', filename, output_file]
    output = Popen(args)
    i += 1


#gm convert -size 600x800 -background white -depth 8 -resize 600x800 \
#    -colorspace gray -type palette -geometry 600x800 \
#    $OUTPUT_DIR/ieroStation.svg $OUTPUT_DIR/kindleStation.png

# create control file
control_file = working_dir2 + 'control.env'

svg_file = open(control_file, "w")

svg_file.write('duration_time=' + duration_time + '\n')
svg_file.write('repeat=' + repeat + '\n')
svg_file.write('display_reset="' + display_reset + '"\n')
svg_file.close()
