#!python

# Run an OCRopus test.
# davep 4-Feb-2013

import sys
import os
import subprocess
import glob
import numpy as np

from basename import get_basename
import drawxml

num_rows_in_strip = 300
seg_method = "rast"
output_dir = None

def parse_runZoneComp_result( strings ) :
#    print strings
#    print type(strings)

    slist = strings.split("\n")
#    print slist
    for s in slist : 
        if s.startswith( "Segmentation Metric" )  :
            fields = s.split()

            metric = float(fields[3])
            return metric

    # TODO add diagnostics, better error report
    raise Exception( "Metric not found" )


#def get_stripnum_from_filename( name ) :
#    fields = name.split("_")
#
#    stripnum = int(fields[1][1:])
#    return stripnum

def get_document_id_from_basename( basename ) :
    # split the basename (e.g., ("A00BZONE_300_010_0000_rast") into just the
    # UW-III document ID
    fields = basename.split("_")
    document_id = fields[0]
    return document_id

def make_output_dir( document_id ) : 
    global output_dir
    
    # create an output directory from numrows, the segmentation method, and the
    # UW-III document_id

    output_dir = "{0}_{1}/{2}/".format( num_rows_in_strip, seg_method, document_id )
    
    if not os.path.exists(output_dir) :
        os.mkdir( output_dir )

def run( imgfilename ) : 
    basename = get_basename(imgfilename)
    
    document_id = get_document_id_from_basename( basename )

    # destination for the output files
    make_output_dir(document_id) 

#    stripnum = get_stripnum_from_filename( basename )

    out_imgfilename = output_dir + "{0}_rast.png".format( basename )
    xml_filename = output_dir + "{0}_rast.xml".format( basename ) 

    input_dir = "{0}/{1}/".format( num_rows_in_strip, document_id )
    
    # zone box files use "ZONE" instead of "BIN"
    # e.g., 
    # A00ABIN_300_010_2990.png -> A00AZONE_300_010_2990.xml 
    gtruth_xml_filename = input_dir + "{0}.xml".format( basename.replace("BIN","ZONE") )

    print "imgfilename=",imgfilename
    print "out_imgfilename=",out_imgfilename
    print "xml_filename=",xml_filename
    print "gtruth_xml_filename=",gtruth_xml_filename
#    sys.exit(0)

    # segment the image
    cmd = "./rast-ocropus {0} {1}".format( imgfilename, out_imgfilename ) 
    print cmd

    try : 
        result = subprocess.check_output( cmd, shell=True )
    except subprocess.CalledProcessError : 
        return (imgfilename,"failed")

    # remove some clutter
    os.unlink(out_imgfilename)

    # write the XML results 
    with open(xml_filename,"w") as outfile :
        print >>outfile, result
    print "wrote", xml_filename

    # run the compare
    cmd = "runZoneComp -g {0} -d {1}".format( gtruth_xml_filename, xml_filename )
    print cmd
    
    result = subprocess.check_output( cmd, shell=True )

    # get the segmentation metric from the output
    metric = parse_runZoneComp_result( result ) 
    print "metric={0}".format( metric )

    # draw the experimental result onto the input image
    out_imgfilename = output_dir + "{0}_rast_zone.png".format( basename )
    fname = drawxml.draw_zones( xml_filename, imgfilename, out_imgfilename )
    print "wrote", fname

    # remove some clutter
#    os.unlink(xml_filename)

    return (imgfilename,metric)

def save_results( data ) : 
    # get an output filename by parsing the first filename in the list
    basename = get_basename( data[0][0] )
    document_id = get_document_id_from_basename( basename ) 

    print document_id

    output_filename = output_dir + document_id + ".dat"

    # get just the valid metrics
    metric_list = []
    num_failures = 0
    for d in data :
        try : 
            metric = float(d[1])
        except ValueError :
            # skip
            metric = 0
            num_failures += 1
        metric_list.append( metric )

    print metric_list
    metric_data = np.asarray( metric_list, dtype="float")
    
    outfile = open(output_filename,"w")

    # write some overall statistics
    print >>outfile, "# id={0}".format( document_id )
    print >>outfile, "# mean={0}".format( np.mean(metric_data) )
    print >>outfile, "# median={0}".format( np.median(metric_data) )
    print >>outfile, "# stddev={0}".format( np.std(metric_data) )
    print >>outfile, "# num_failures={0}".format( num_failures)

    for d in data : 
        basename = get_basename(d[0])
        print >>outfile, basename,d[1]
    outfile.close()

#    with open(output_filename,"w") as outfile : 
#        for d in data : 
#            # print the metric
#            print >>outfile, "{0}".format( d[1] )

def main() : 

#    for imgfilename in sys.argv[1:] : 
#        run( imgfilename ) 

    data = [ run(f) for f in sys.argv[1:] ]
    print data

    save_results( data ) 

if __name__=='__main__' :
    main()


