#!/usr/bin/python

# Parse an OCRopus zone output XML.
# Draw zones onto an image.
# davep 21-Jan-2013

import sys
import os
import Image
import ImageDraw

import gtruthxml
from basename import get_basename

def load_image( imgfilename ) : 
    img = Image.open(imgfilename)
    img.load()
    if img.mode != "RGB" :
        img2 = img.convert("RGB")
        img = img2
        del img2

    return img

def draw_zones( xmlfilename, imgfilename, outfilename=None ) : 

    img = load_image( imgfilename ) 

    draw = ImageDraw.Draw(img)

    zone_list = gtruthxml.parse_xml( xmlfilename ) 

    for zone in zone_list : 
        if zone.value=="Non-text" :
            color = "red"
        else :
            color = "green"

        x1 = zone.rect[0].x
        y1 = zone.rect[0].y
        x2 = zone.rect[2].x
        y2 = zone.rect[2].y
        draw.rectangle( ((x1,y1),(x2,y2)), outline=color)

    if outfilename is None : 
        outfilename = get_basename( imgfilename )+"_zones.png"
    img.save(outfilename)
    return outfilename

def main() : 
    xmlfilename = sys.argv[1]
    imgfilename = sys.argv[2]

    outfilename = draw_zones( xmlfilename, imgfilename ) 
    print "wrote", outfilename

if __name__=='__main__':
    main()

