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
        # self.value will be "Text", "Non-text", ... (more later)
        self.value = None

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

#        else : 
#            # TODO make this smarter (defaults?)
#            raise Exception( "need width/height or box parameters" )

        # add enough duck so zone2xml can quack me 
        # http://en.wikipedia.org/wiki/Duck_typing
        # upper left 
        self._corner_one = { "row": self.rect[0].y, "col": self.rect[0].x } 
        # lower right
        self._corner_two = { "row": self.rect[2].y, "col": self.rect[2].x } 

    def set_value( self, value ) : 
        # set the strip contents type
        if value not in ("Text","Non-text") : 
            raise Exception( "Unknown strip content type {0}".format( value ) )
        self.value = value

    def next_strip( self ) : 
        # increment to the next strip
        self.rect[0].y += self.height
        self.rect[1].y += self.height
        self.rect[2].y += self.height
        self.rect[3].y += self.height

    def __repr__( self ) : 
        return str(self.rect)

    def __getattr__( self, name ) : 
        if name=="corner_one" : 
            self._corner_one = { "row": self.rect[0].y, "col": self.rect[0].x } 
            return self._corner_one
        elif name=="corner_two" : 
            self._corner_two = { "row": self.rect[2].y, "col": self.rect[2].x } 
            return self._corner_two
        else :
            raise AttributeError


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

def box_list_bounding_box( box_list ) :
    # find a bounding box that encompasses all boxes in the box_list
    
    min_row = sys.maxint
    min_col = sys.maxint
    max_row = 0
    max_col = 0

    for box in box_list :
        if box.corner_one["row"] < min_row :
            min_row = box.corner_one["row"]
        if box.corner_one["col"] < min_col :
            min_col = box.corner_one["col"]

        if box.corner_two["row"] > max_row :
            max_row = box.corner_two["row"]
        if box.corner_two["col"] > max_col :
            max_col = box.corner_two["col"]

    return {"upper_left": {"row":min_row,"col":min_col},
            "lower_right":{"row":max_row,"col":max_col} }

def slice_boxes( boxfilename) : 
    # iterate through a box list, making strip slices.
    
    box_list = zonebox.load_boxes(boxfilename)
#    for box in box_list :
#        print box
#        s = Strip(box=box)
#        print s

    # find the largest Y index in our boxes (the maximum row)
    bounding_box = box_list_bounding_box( box_list )
    print "bounding_box=",bounding_box

    # use lower left row count as the number of rows we will iterate
    num_rows = bounding_box["lower_right"]["row"]
    print "num_rows=",num_rows

    # make a starting strip
    num_rows_in_strip = 300
    s = Strip(width=2560,height=num_rows_in_strip)

    row = 0
    while row < num_rows : 
        print "strip=",s
        for box in box_list : 
            print "box=",box
            isect = strip_intersect( Strip(box=box), s )
            if isect : 
                print "intersect=",isect
            else :
                print "no intersections"

        s.next_strip()
        row += num_rows_in_strip

def main() : 
    boxfilename = sys.argv[1]

    slice_boxes( boxfilename)

if __name__ == '__main__' :
    main()

