#!/usr/bin/python

# Parse an OCRopus output XML.
# davep 09-Feb-2013

import sys
import os
import xml.etree.ElementTree as ET

import rects

def load_xml( xmlfilename ) :
    tree = ET.parse(xmlfilename)
    root = tree.getroot()
    return root

# pretend to be a UW-III boxfile so I can convert an upper_left/lower_right to
# a rects.Strip
class Zone( object ): 
    corner_one = {"row":0,"col":0}
    corner_two = {"row":0,"col":0}

    def __init__( self, upper_left, lower_right ) : 
        # incoming fields are x,y order 
        self.corner_one["row"] = upper_left[1]
        self.corner_one["col"] = upper_left[0]
        self.corner_two["row"] = lower_right[1]
        self.corner_two["col"] = lower_right[0]

def parse_xml( xmlfilename ) : 

    root = load_xml( xmlfilename ) 

    rect_list = []

    for child in root : 
        for zone in child : 
            if zone.tag=="Classification" : 

                # send our pretend Box class so we can leverage the rects.Strip
                rect = rects.Strip( box=Zone((x1,y1),(x2,y2)) )
                rect.set_value( zone[0].attrib["Value"] )
                rect_list.append( rect ) 
                rect = None

            elif zone.tag=="ZoneCorners" : 
                # upper left
                x1,y1=zone[0].attrib["x"], zone[0].attrib["y"]
                x1 = float(x1)
                y1 = float(y1)
                # lower right
                x2,y2=zone[-2].attrib["x"], zone[-2].attrib["y"]
                x2 = float(x2)
                y2 = float(y2)

    return rect_list

def main() : 
    for xmlfilename in sys.argv[1:]:
        rect_list = parse_xml( xmlfilename )
        print rect_list

if __name__=='__main__':
    main()

