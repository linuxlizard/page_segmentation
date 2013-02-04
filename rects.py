#!python

# Parse a UWIII ground truth Box file. Slice into 1",2",3",4",etc new ground
# truth files.
#
# davep 01-Feb-2013

import sys
import os

import zonebox

class Point(object):
    def __init__(self):
        self.x = 0
        self.y = 0

    def __repr__(self) : 
        return "({0},{1})".format(self.x,self.y)

class Strip( object ) :
    def __init__( self, **kwargs ) : 
        self.rect = [ Point(), Point(), Point(), Point() ]

        if "width" in kwargs and "height" in kwargs :
            # create a strip from a simple width/height
            width = kwargs["width"]
            height = kwargs["height"]
            self.rect[0].x = 0
            self.rect[0].y = 0
            self.rect[1].x = width
            self.rect[1].y = 0
            self.rect[2].x = width
            self.rect[2].y = height
            self.rect[3].x = 0
            self.rect[3].y = height

            self.width = width
            self.height = height
        elif "box" in kwargs : 
            # create a strip from a UW-III ZoneBox class
            box = kwargs["box"]

            self.rect[0].x = box.corner_one["col"]
            self.rect[0].y = box.corner_one["row"]

            self.rect[1].x = box.corner_two["col"] # same as [2]
            self.rect[1].y = box.corner_one["row"] # same as [0]

            self.rect[2].x = box.corner_two["col"]
            self.rect[2].y = box.corner_two["row"]

            self.rect[3].x = box.corner_one["col"]  # same as [0]
            self.rect[3].y = box.corner_two["row"]  # same as [2]

            self.width = self.rect[1].x - self.rect[0].x
            self.height = self.rect[2].y - self.rect[1].y

    def next_strip( self ) : 
        # increment to the next strip
        self.rect[0].y += self.height
        self.rect[1].y += self.height
        self.rect[2].y += self.height
        self.rect[3].y += self.height

    def __repr__( self ) : 
        return str(self.rect)

def strip_intersect( gtruth, strip ) : 
    intersect = Strip()

    # clockwise from upper left 0 -> 1 
    #                           |    |
    #                           3 <- 2

    # null set? (no intersection)
    # if gtruth lower right is above strip
    #    or gruth upper left is below strip
    if gtruth.rect[2].y < strip.rect[0].y \
       or gtruth.rect[0].y > strip.rect[2].y :
       return None


    # upper left
    intersect.rect[0].x = max(gtruth.rect[0].x,strip.rect[0].x)
    intersect.rect[0].y = max(gtruth.rect[0].y,strip.rect[0].y)

    # upper right
    intersect.rect[1].x = min(gtruth.rect[1].x,strip.rect[1].x)
    intersect.rect[1].y = max(gtruth.rect[1].y,strip.rect[1].y)

    # lower right
    intersect.rect[2].x = min(gtruth.rect[2].x,strip.rect[2].x)
    intersect.rect[2].y = min(gtruth.rect[2].y,strip.rect[2].y)

    # lower left
    intersect.rect[3].x = max(gtruth.rect[3].x,strip.rect[3].x)
    intersect.rect[3].y = min(gtruth.rect[3].y,strip.rect[3].y)

    return intersect

def slice_boxes( boxfilename) : 
    box_list = zonebox.load_boxes(boxfilename)
    for box in box_list :
        print box
        s = Strip(box=box)
        print s

    s = Strip(width=2560,height=300)
    print "strip=",s
    s.next_strip()
    print "next=",s

    isect = strip_intersect( Strip(box=box_list[0]), s )
    print "intersect=",isect

def main() : 
    boxfilename = sys.argv[1]

    slice_boxes( boxfilename)

if __name__ == '__main__' :
    main()

