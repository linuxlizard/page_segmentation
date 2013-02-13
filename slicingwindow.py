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
import os

import mkslices
from basename import get_basename
import rects
import zonebox
import zone2xml
import gtruthxml

num_rows_in_strip = 600
num_rows_to_slide  = 20
#output_dir = str(num_rows_in_strip)

def write_image( data, outfilename ) : 
    img = Image.fromarray( data, mode="L" )
    img.save( outfilename ) 

def make_all_strips_images( data, basename, output_dir ) :
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

def make_all_gtruth_xml( box_strip_list, data, output_dir, basename) : 

    total_num_rows,num_cols = data.shape

    # starting strip as wide as the iamge with our base number of rows
    s = rects.Strip(width=num_cols, height=num_rows_in_strip )

    outfilename_fmt = "{0}_{1:03}_{2:03}_{3:04}.xml"

    row = 0

    while row < total_num_rows : 

        # linear search all the boxes searching for those that match this strip
        box_intersect_list = []
        for box_strip in box_strip_list : 
            isect = rects.strip_intersect( box_strip, s )
            if not isect : 
                continue

#            print 'isect=',isect

            # adjust the intersections so the new ground truth of the box
            # intersections starts at row=0 (making new images out of
            # strips so need ground truth for each image strip)
            for rect in isect.rect : 
                # subtract out the starting Y position of upper left
                rect.y -= s.rect[0].y
#            print "adjusted isect=",isect

            # save this intersection; we'll write to a new XML file 
            box_intersect_list.append( isect )

        # save the intersections as XML
        xmlfilename = os.path.join(output_dir, outfilename_fmt.format( 
                basename, num_rows_in_strip, num_rows_to_slide, row ) )
#        xmlfilename = output_dir + "/" + outfilename_fmt.format( 
#                basename, num_rows_in_strip, num_rows_to_slide, row )
#        print xmlfilename

        with open(xmlfilename,"w") as outfile :
            zone2xml.write_boxlist_to_xml( outfile, box_intersect_list )
        print "wrote", xmlfilename


        # slide the strip down by our window shift amount
        s.rect[0].y += num_rows_to_slide
        s.rect[1].y += num_rows_to_slide
        s.rect[2].y += num_rows_to_slide
        s.rect[3].y += num_rows_to_slide

        row += num_rows_to_slide

def make_output_dir( basename ) : 
    # output dir path is "stripsize/basename/"
    # e.g., "300/A00BZONE"
    
#    global output_dir
    
    output_dir = os.path.join( str(num_rows_in_strip), basename )
#    output_dir = "{0}/{1}/".format( num_rows_in_strip, basename )

    if os.path.exists( output_dir ) :
        return output_dir

    os.mkdir( output_dir )

    return output_dir

def make_sliding_strips_from_box( boxfilename ) :
    basename = get_basename( boxfilename )

    # create the output directory for all the files I'm about to create
    output_dir = make_output_dir(basename)
#    return
    
    box_list = zonebox.load_boxes( boxfilename ) 

    # load the image associated with this box list
    # assume all the boxes have the same image name (they should)
    imgfilename = "IMAGEBIN/{0}BIN.png".format( box_list[0].document_id )

    # get the image as a numpy array
    data = mkslices.load_image( imgfilename )

    strip_list = make_all_strips_images( data, basename, output_dir )

    # 
    # Now make the ground truth files for each strip
    #
    
    # convert the box list into a list of strips
    box_strip_list = [ rects.Strip(box=box) for box in box_list ]

    # slice up the ground truth into individual XML files 
    make_all_gtruth_xml( box_strip_list, data, output_dir, basename ) 

def make_sliding_strips_from_image( imgfilename, output_dir ) : 
    basename = get_basename( imgfilename ) 

    # get the image as a numpy array
    data = mkslices.load_image( imgfilename )
    strip_list = make_all_strips_images( data, basename, output_dir )

def awinder( ) : 
    # slice up Amy Winder's images 
    output_dir_base = "{0}_winder/".format(num_rows_in_strip)
#    output_dir_base = "300_winder/"

    for imgfilename in sys.argv[1:] :
        basename = get_basename(imgfilename)

        input_path = os.path.dirname(imgfilename)
        # get rid of the trailing "/png" component (it's annoying)
        input_path = input_path.replace( "/png", "/" )

        output_dir = output_dir_base + input_path + basename
        print output_dir

        if os.path.exists(output_dir) : 
            print "{0} exists so assume files are OK".format(output_dir)
            continue
        else:
            os.makedirs(output_dir)

        make_sliding_strips_from_image( imgfilename, output_dir )

        xmlfilename = imgfilename.replace(".png",".xml")
        xmlfilename = xmlfilename.replace("png","gTruth")
        print xmlfilename

        try : 
            zone_list = gtruthxml.parse_xml( xmlfilename )
        except IOError,e:
            if e.errno==2 :
                # some of the files are living in a ./xml subdir
                xmlfilename = imgfilename.replace(".png",".xml")
                xmlfilename = xmlfilename.replace("png","gTruth/xml")
                zone_list = gtruthxml.parse_xml( xmlfilename )
            else :
                raise

        print zone_list

        # get the image as a numpy array
        data = mkslices.load_image( imgfilename )

        # slice up the ground truth into individual XML files 
        make_all_gtruth_xml( zone_list, data, output_dir, basename ) 

def main() : 
    for boxfilename in sys.argv[1:] :
        make_sliding_strips_from_box( boxfilename )

if __name__=='__main__': 
    main()
#    awinder()

