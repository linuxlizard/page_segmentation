#!python

# Read UW-III Zone BOX file. Convert to OCRopus zone XML. 
# davep 27-Jan-2013

#import os
import sys

import zonebox

def print_vertices( outfile, zonebox ) : 
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
        print >>outfile, "<Vertex x=\"{0}\" y=\"{1}\">".format( p["col"],p["row"])
        print >>outfile, "</Vertex>"

def print_zone_corners( outfile, zonebox ) : 
    print >>outfile, "<ZoneCorners>"
    print_vertices( outfile, zonebox ) 
    print >>outfile, "</ZoneCorners>"

def print_zone_classification( outfile, zonebox ) : 
    print >>outfile, "<Classification>"
    # nothing in the zonebox indicates text/graphics so mark everything as text
    # for now
    print >>outfile, "<Category Value=\"Text\">"
    print >>outfile, "</Category>"
    print >>outfile, "</Classification>"

def print_zone( outfile, zonebox ) : 
    print >>outfile, "<Zone>"
    print_zone_corners( outfile, zonebox ) 
    print_zone_classification( outfile, zonebox )
    print >>outfile, "</Zone>"

def write_boxlist_to_xml( outfile, box_list ) : 
    print >>outfile, "<Page>"
    for box in box_list : 
        print_zone( outfile, box ) 
    print >>outfile, "</Page>"
    

def convert_zonebox_to_xml( outfile, boxfilename) : 

    box_list = zonebox.load_boxes(boxfilename)

    write_boxlist_to_xml( outfile, box_list )

def main() : 
    boxfilename = sys.argv[1]

    convert_zonebox_to_xml( sys.stdout, boxfilename ) 
    
    
if __name__=='__main__' : 
    main()

