#!python

# Slice a window of N rows down an image by M rows (the slide) each step.
# Write each strip to an individual image file in a subdirectory.
#
# created for the page segmentation comparisson
#
# davep 5-Feb-2013

import sys
import numpy as np
import Image

import mkslices
from basename import get_basename

num_rows_in_strip = 300
num_rows_to_slide  = 10
output_dir = str(num_rows_in_strip)

def write_image( data, outfilename ) : 
    img = Image.fromarray( data, mode="L" )
    img.save( outfilename ) 

def make_all_strips( data, basename ) :
    # carve up the numpy array into N strips of num_rows each; return an array
    # of said strips

    start_idx = 0
    end_idx = start_idx + num_rows_in_strip

    outfilename_fmt = "{0}_{1:03}_{2:03}_{3:04}.png"

    print "make_strips shape=",data.shape
    strip_list = []
    total_num_rows = data.shape[0] 
    while start_idx < total_num_rows : 
        # kill any previous reference to something in the strip_list
        s = None 

        s = data[start_idx:end_idx,:] 
        print "start={0} end={1} s={2}".format( start_idx, end_idx, s.shape )
        strip_list.append( s ) 

        outfilename = output_dir + "/" + outfilename_fmt.format( 
                basename, num_rows_in_strip, num_rows_to_slide, start_idx )
        print outfilename
        write_image( s, outfilename )
                
        start_idx += num_rows_to_slide
        end_idx = min( total_num_rows, end_idx+num_rows_to_slide )

    return strip_list


def make_sliding_strips( imgfilename ) :
    data = mkslices.load_image( imgfilename )

    basename = get_basename( imgfilename ) 

    strip_list = make_all_strips( data, basename )


def main() : 
    imgfilename = sys.argv[1]
    make_sliding_strips( imgfilename )

if __name__=='__main__': 
    main()

