#!/usr/bin/python

# Parse an OCRopus zone output XML.
# Draw zones onto an image.
# davep 21-Jan-2013

import sys
import os
import Image
import ImageDraw
import xml.etree.ElementTree as ET

def get_basename( filename ) : 
    return os.path.splitext( os.path.split( filename )[1] )[0]

def main() : 
    xmlfilename = sys.argv[1]
    imgfilename = sys.argv[2]
#    xmlfilename = "rast.xml"
#    xmlfilename = "vor.xml"
#    imgfilename = "1col300_1.png"

    img = Image.open(imgfilename)
    img.load()
    if img.mode != "RGB" :
        img2 = img.convert("RGB")
        img = img2
        del img2
    draw = ImageDraw.Draw(img)

    tree = ET.parse(xmlfilename)
    root = tree.getroot()
    print root

    for child in root : 
        print child.tag, child.attrib
        for zone in child : 
            print "   ",zone.tag,zone.attrib
            if zone.tag=="Classification" : 
                print "      ",zone[0].tag, zone[0].attrib

                if zone[0].attrib["Value"]=="Non-text" :
                    color = "red"
                else :
                    color = "green"
                print "color=",color
                draw.rectangle( ((x1,y1),(x2,y2)), outline=color)

            elif zone.tag=="ZoneCorners" : 
                for corners in zone : 
                    print "      ",corners.tag, corners.attrib
                x1,y1=zone[0].attrib["x"], zone[0].attrib["y"]
                x1 = float(x1)
                y1 = float(y1)
                x2,y2=zone[-2].attrib["x"], zone[-2].attrib["y"]
                x2 = float(x2)
                y2 = float(y2)

    outfilename = get_basename( imgfilename )+"_zones.png"
    img.save(outfilename)
    print "wrote", outfilename

if __name__=='__main__':
    main()

