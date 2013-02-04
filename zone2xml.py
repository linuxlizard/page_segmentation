#!python

# Read UW-III Zone BOX file. Convert to OCRopus zone XML. 
# davep 27-Jan-2013

#import os
import sys

import zonebox

def print_vertices( zonebox ) : 
    # UWIII ZoneBox contains upper-left and lower-right corners.
    # Need to convert to four points.
    # [0] is x
    # [1] is y
    #
    # p0 -> p1
    # ^     |
    # |     V
    # p3 <- p2

    p0 = zonebox.corner_one  # upper left
    p2 = zonebox.corner_two  # lower right

    # upper right 
    p1 = { "row" : p2["row"],
           "col" : p0["col"] }

    # lower left 
    p3 = { "row" : p0["row"],
           "col" : p2["col"] }
#    p3 = (p0[0],p2[1])

    for p in (p0,p1,p2,p3) : 
        print "<Vertex x=\"{0}\" y=\"{1}\">".format( p["col"],p["row"])
        print "</Vertex>"

def print_zone_corners( zonebox ) : 
    print "<ZoneCorners>"
    print_vertices( zonebox ) 
    print "</ZoneCorners>"

def print_zone_classification( zonebox ) : 
    print "<Classification>"
    # nothing in the zonebox indicates text/graphics so mark everything as text
    # for now
    print "<Category Value=\"Text\">"
    print "</Category>"
    print "</Classification>"

def print_zone( zonebox ) : 
    print "<Zone>"
    print_zone_corners( zonebox ) 
    print_zone_classification( zonebox )
    print "</Zone>"

def convert_zonebox_to_xml( boxfilename) : 

    box_list = zonebox.load_boxes(boxfilename)

    print "<Page>"
    for box in box_list : 
        print_zone( box ) 
    print "</Page>"
    

def main() : 
    boxfilename = sys.argv[1]

    convert_zonebox_to_xml( boxfilename ) 
    
    
if __name__=='__main__' : 
    main()

