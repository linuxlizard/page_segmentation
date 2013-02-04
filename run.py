#!python

# Run an OCRopus test.
# davep 4-Feb-2013

import sys
import os
import subprocess
import glob

from basename import get_basename

gtruth_xml_basename = "A00BZONE"

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

    out_imgfilename = "{0}_rast.png".format( basename )
    xml_filename = "{0}_rast.xml".format( basename ) 

    gtruth_xml_filename = "{0}_s{1}.xml".format( gtruth_xml_basename, stripnum )

    print imgfilename, out_imgfilename, xml_filename, gtruth_xml_filename
#    sys.exit(0)

    # segment the image
    cmd = "./rast-ocropus {0} {1}".format( 
                imgfilename, out_imgfilename ) 

    # remove some clutter
    os.unlink(out_imgfilename)

    print cmd
    result = subprocess.check_output( cmd, shell=True )

#    print result

    with open(xml_filename,"w") as outfile :
        print >>outfile, result
    print "wrote", xml_filename

    # run the compare
    cmd = "runZoneComp -g {0} -d {1}".format( 
            gtruth_xml_filename, xml_filename )

    print cmd
    result = subprocess.check_output( cmd, shell=True )

    metric = parse_runZoneComp_result( result ) 
    print "{0},{1}".format( imgfilename, metric )

    return (imgfilename,metric)

def main() : 

#    for imgfilename in sys.argv[1:] : 
#        run( imgfilename ) 

    data = [ run(f) for f in sys.argv[1:] ]
    print data

    with open("data.dat","w") as outfile : 
        for d in data : 
            # print the metric
            print >>outfile, "{0}".format( d[1] )

if __name__=='__main__' :
    main()


