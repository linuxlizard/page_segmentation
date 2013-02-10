#!python

# Load an image. Break apart into multiple images of 1", 2", 3", 4", 6" strips.
# davep 29-Jan-2013

import sys
import os
import numpy as np
import Image

from basename import get_basename

def make_slices( data, num_rows_in_slice ) :
    # carve up the numpy array into N strips of num_rows each; return an array
    # of said strips

    start_idx = 0
    end_idx = start_idx + num_rows_in_slice

    print "make_slices shape=",data.shape
    slice_list = []
    total_num_rows = data.shape[0] 
    while start_idx < total_num_rows : 
        s = data[start_idx:end_idx,:]
        print "start={0} end={1} s={2}".format( start_idx, end_idx, s.shape )
        slice_list.append( s ) 
        s = None

        start_idx += num_rows_in_slice
        end_idx = min( total_num_rows, end_idx+num_rows_in_slice )

    return slice_list

def load_image( imgfilename ) : 
    img = Image.open(imgfilename)
    img.load()
    
    if img.mode == "RGB" : 
        errmsg="mode={0}; cowardly refusing a non-gray image".format( img.mode )
        raise Exception( errmsg )

    # single bit image? So much I don't know. I don know unless I convert to an
    # 8bpp gray, the numpy conversion gets... weird.
    if img.mode == "1" :
        img2 = img.convert("L")
        img = img2
        del img2

    basename = get_basename( imgfilename )

    data = np.asarray(img,dtype="uint8")
    print "shape=",data.shape

    return data

def make_image_slices( imgfilename, num_rows=300 ) :

    imgslices = make_slices( data, num_rows )

    outfilename_list = []
    outfilename_fmt = "{0}_s{1}.png"
    for idx,n in enumerate(imgslices) : 
        print n.shape
        outfilename = outfilename_fmt.format( basename, idx )

        outimg = Image.fromarray( n, "L" )
        outimg.save( outfilename )
        print "wrote", outfilename 
        outfilename_list.append( outfilename )

    return outfilename_list

def main() : 
    for imgfilename in sys.argv[1:] :
        make_image_slices( imgfilename )

if __name__=='__main__': 
    main()

