#!/usr/bin/python

# Parse an OCRopus zone output XML.
# Draw zones onto an image.
# davep 21-Jan-2013

import sys
import os
import Image
import ImageDraw
import xml.etree.ElementTree as ET

from basename import get_basename

def load_xml( xmlfilename ) :
    tree = ET.parse(xmlfilename)
    root = tree.getroot()
    return root

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

    root = load_xml( xmlfilename ) 

    for child in root : 
        for zone in child : 
            if zone.tag=="Classification" : 

                if zone[0].attrib["Value"]=="Non-text" :
                    color = "red"
                else :
                    color = "green"
                draw.rectangle( ((x1,y1),(x2,y2)), outline=color)

            elif zone.tag=="ZoneCorners" : 
                x1,y1=zone[0].attrib["x"], zone[0].attrib["y"]
                x1 = float(x1)
                y1 = float(y1)
                x2,y2=zone[-2].attrib["x"], zone[-2].attrib["y"]
                x2 = float(x2)
                y2 = float(y2)

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

