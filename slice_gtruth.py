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
import numpy as np

import zonebox
import rects
import drawboxes
from basename import get_basename
import mkslices
import zone2xml

strip_rows = 300

def make_gtruth_slices( boxfilename ) : 
    basename = get_basename( boxfilename )

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
    s = rects.Strip(width=num_cols, height=strip_rows )

    box_strip_list = [ rects.Strip(box=box) for box in box_list ]

    data = np.asarray(img,dtype="uint8")
    print "shape=",data.shape

    # draw the ground truth in blue as sanity check (should see no blue in the
    # output image)
    for box_strip in box_strip_list : 
        upper_left = box_strip.rect[0].x, box_strip.rect[0].y
        lower_right = box_strip.rect[2].x, box_strip.rect[2].y

        draw.rectangle( (upper_left,lower_right), outline="blue")

    # iterate the strip down the page, calculating all the box intersections
    # for each strip
    row = 0
    strip_counter = 0
    while row < num_rows : 
        print "strip=",s

        upper_left = s.rect[0].x, s.rect[0].y
        lower_right = s.rect[2].x, s.rect[2].y
        draw.rectangle( (upper_left,lower_right), outline="green" )

        # linear search all the boxes searching for those that match this strip
        box_intersect_list = []
        for box_strip in box_strip_list : 
            isect = rects.strip_intersect( box_strip, s )
            if isect : 
                print 'isect=',isect

                # PIL's Draw is x,y order
                upper_left = isect.rect[0].x, isect.rect[0].y
                lower_right = isect.rect[2].x, isect.rect[2].y

                draw.rectangle( (upper_left,lower_right), outline="red" )

                box_intersect_list.append( isect )

        # save the intersections as XML
        xmlfilename = "{0}_s{1}.xml".format( basename, strip_counter )
        with open(xmlfilename,"w") as outfile :
            zone2xml.write_boxlist_to_xml( outfile, box_intersect_list )
        print "wrote", xmlfilename

        s.next_strip()
        row += strip_rows
        strip_counter += 1

    outfilename = "{0}_out.png".format( basename )
    img.save(outfilename)
    print "wrote",outfilename

    # write all the image slices
#    mkslices.make_image_slices( imgfilename, strip_rows )

def main() : 
    boxfilename = sys.argv[1]
    make_gtruth_slices( boxfilename )

if __name__=='__main__': 
    main()

