#!python

# Given a .BOX file, read the associated image. Slice the image into strips of
# 'N' rows. Write each image strip to new file. 
#
# Also create new ground truth rectangles. Write the ground truth rectangles to
# zone XML file.
#
# davep 03-Feb-2013

import sys
import os
import Image
import ImageDraw

import zonebox
import rects
from rects import Strip
import drawboxes

strip_rows = 300

def make_gtruth_slices( boxfilename ) : 

    box_list = zonebox.load_boxes( boxfilename ) 
    print "found",len(box_list),"boxes"

    # load the image associated with this box list
    # assume all the boxes have the same image name (they should)
    imgfilename = "IMAGEBIN/{0}BIN.png".format( box_list[0].document_id )

    img = drawboxes.load_image(imgfilename)
    print img.mode, img.size
    num_cols,num_rows = img.size
    print "rows={0} cols={1}".format( num_rows, num_cols )

    draw = ImageDraw.Draw(img)
    
    # starting strip as wide as the iamge with our base number of rows
    s = Strip(width=num_cols, height=strip_rows )

    box_strip_list = [ Strip(box=box) for box in box_list ]

    # iterate the strip down the page, calculating all the box intersections
    # for each strip
    row = 0
    while row < num_rows : 
        print "strip=",s

        upper_left = s.rect[0].x, s.rect[0].y
        lower_right = s.rect[2].x, s.rect[2].y
        draw.rectangle( (upper_left,lower_right), outline="green" )

        for box_strip in box_strip_list : 
            isect = rects.strip_intersect( box_strip, s )
            if isect : 
                print isect

                # PIL's Draw is x,y order
                upper_left = isect.rect[0].x, isect.rect[0].y
                lower_right = isect.rect[2].x, isect.rect[2].y

                draw.rectangle( (upper_left,lower_right), outline="red" )

                break

        s.next_strip()
        row += strip_rows

    outfilename = "out.png"
    img.save(outfilename)
    print "wrote",outfilename

def main() : 
    boxfilename = sys.argv[1]
    make_gtruth_slices( boxfilename )

if __name__=='__main__': 
    main()

