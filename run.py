#!python

# Run an OCRopus test.
# davep 4-Feb-2013

import sys
import os
import subprocess
import glob

from basename import get_basename
import drawxml

result_dir = "300_rast"

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


def get_stripnum_from_filename( name ) :
    fields = name.split("_")

    stripnum = int(fields[1][1:])
    return stripnum

def run( imgfilename ) : 
    basename = get_basename(imgfilename)
    
    stripnum = get_stripnum_from_filename( basename )

    out_imgfilename = result_dir + "/" + "{0}_rast.png".format( basename )
    xml_filename = result_dir + "/" + "{0}_rast.xml".format( basename ) 

    # zone box files use "ZONE" instead of "BIN"
    # e.g., 
    # A00ABIN_300_010_2990.png -> A00AZONE_300_010_2990.xml 
    gtruth_xml_filename = "300/{0}.xml".format( basename.replace("BIN","ZONE") )

    print imgfilename, out_imgfilename, xml_filename, gtruth_xml_filename
#    sys.exit(0)

    # segment the image
    cmd = "./rast-ocropus {0} {1}".format( imgfilename, out_imgfilename ) 
    print cmd

    result = subprocess.check_output( cmd, shell=True )

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
    out_imgfilename = result_dir + "/" + "{0}_rast_zone.png".format( basename )
    fname = drawxml.draw_zones( xml_filename, imgfilename, out_imgfilename )
    print "wrote", fname

    # remove some clutter
#    os.unlink(xml_filename)

    return (imgfilename,metric)

def main() : 

#    for imgfilename in sys.argv[1:] : 
#        run( imgfilename ) 

    data = []

    outfile = open("data.dat","w")

    for f in sys.argv[1:] :
        filename,metric = run(f)
        print >>outfile, "{0}".format( metric )
        outfile.flush()

    outfile.close()
    return

    data = [ run(f) for f in sys.argv[1:] ]
    print data

    with open("data.dat","w") as outfile : 
        for d in data : 
            # print the metric
            print >>outfile, "{0}".format( d[1] )

if __name__=='__main__' :
    main()


