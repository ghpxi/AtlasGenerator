#!/usr/bin/env python

# Script Name       : ag.py
# Author            : ghpxi
# Created           : 23th May 2015
# Last Modified     : 
# Version           : 1.0
# Description       : generate png atlas

import os
import sys
import getopt

from glob import glob
from PIL import Image


BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class Node(object):
    def __init__(self, img, w, h, offx, offy):
        self.img = img
        self.w = w
        self.h = h
        self.offx = offx
        self.offy = offy
        self.child = {0: None, 1: None}

    def insert(self, img, w, h):
        if self.img is not None:
            return False

        if self.child[0] is not None or self.child[1] is not None:
            return self.child[0].insert(img, w, h) or \
                   self.child[1].insert(img, w, h)
        else:
            if w == self.w and h == self.h:
                self.img = img
                return self.offx, self.offy
            elif w <= self.w and h <= self.h:
                dw = self.w - w
                dh = self.h - h

                if dw >= dh:
                    self.child[0] = Node(None, w, self.h, self.offx, self.offy)
                    self.child[1] = Node(None, dw, self.h, self.offx + w, self.offy)
                else:
                    self.child[0] = Node(None, self.w, h, self.offx, self.offy)
                    self.child[1] = Node(None, self.w, dh, self.offx, self.offy + h)

                return self.child[0].insert(img, w, h)

            return False


class Atlas(object):
    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.node = Node(None, width, height, 0, 0)

        self.positions = []
        self.missed = []

    def add(self, img):
        result = self.node.insert(img, img.size[0] + 1, img.size[1] + 1)

        if not result:
            self.missed.append(img)
            
            print 'missed `%s`' % img.filename.split('/')[-1]
        else:
            self.positions.append({'img': img, 'pos': result})

    def save(self, png_filename, map_filename):
        atlas_img = Image.new('RGBA', (self.width, self.height))
        atlas_map = open(map_filename, 'w')

        for p in self.positions:
            filename = p['img'].filename.split('/')[-1]
            data = {
                'filename': filename,
                'left': p['pos'][0],
                'top': p['pos'][1],
                'width': p['img'].size[0],
                'height': p['img'].size[1],
            }

            atlas_img.paste(p['img'], p['pos'])
            atlas_map.write('{filename} \n'
                            '\toffx:   {left}\n'
                            '\toffy:   {top}\n'
                            '\twidth:  {width}\n'
                            '\theight: {height}\n\n'.format(**data))

        atlas_img.save(png_filename, 'png')
        atlas_map.close()


def main(opts):
    png_files = glob(os.path.join(opts['dir'], '*.png'))

    atlas = Atlas(opts['width'], opts['height'])

    pngs = [Image.open(p) for p in png_files]
    for png in sorted(pngs, key=lambda s: s.size[0] * s.size[1])[::-1]:
        atlas.add(png)

    atlas.save('atlas.png', 'map.txt')


def parse_options(argv):
    options = {
        'dir': '',
        'width': 1024,
        'height': 1024,
        'css': False,
    }

    try:
        opts, args = getopt.getopt(argv, 'd:w:h:', ['directory=', 'width=', 'height=', 'help'])
    except getopt.GetoptError as err:
        sys.exit(str(err))

    for opt, val in opts:
        if opt == '--help':
            pass
        elif opt == '--css':
            options['css'] = True
        elif opt in ('-d', '--directory'):
            options['dir'] = os.path.join(BASE_DIR, val)
            if not os.path.exists(options['dir']):
                sys.exit('Directory %s not exists' % options['dir'])
        elif opt in ('-w', '--width'):
            try:
                options['width'] = int(val)
            except ValueError:
                sys.exit('Width must be integer value greater than zero')
        elif opt in ('-h', '--height'):
            try:
                options['height'] = int(val)
            except ValueError:
                sys.exit('Height must be integer value greater than zero')
        else:
            sys.exit('unhandled option')

    return options


if __name__ == '__main__':
    main(parse_options(sys.argv[1:]))