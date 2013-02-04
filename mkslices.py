#!python

# Load an image. Break apart into multiple images of 1", 2", 3", 4", 6" strips.
# davep 29-Jan-2013

import sys
import os
import numpy as np
import Image

def get_basename( filename ) : 
    return os.path.splitext( os.path.split( filename )[1] )[0]

def make_slices( data, num_rows ) :
    # carve up the numpy array into N strips of num_rows each; return an array
    # of said strips

    start_idx = 0
    end_idx = start_idx + num_rows

    slice_list = []
    while start_idx < data.shape[1] : 
        s = data[start_idx:end_idx,:]
        print "s=",s.shape
        slice_list.append( s ) 
        s = None

        start_idx += num_rows
        end_idx = min( data.shape[1], end_idx+num_rows )

    return slice_list


def make_image_slices( imgfilename ) :
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

    imgslices = make_slices( data, 600 )

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
    imgfilename = sys.argv[1]
    make_image_slices( imgfilename )

if __name__=='__main__': 
    main()

