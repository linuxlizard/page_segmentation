#!python

# Run the segmentation then zone compare on a UW-III image. Capture the output
# metric. 
#
# davep 6-Feb-2013

import sys
import subprocess
import os
import pickle
import glob
import Image
import argparse
import signal

from basename import get_basename 
import drawxml

output_dir = "/tmp/"

num_rows = 300
uwiii_imgdir = "IMAGEBIN/"
uwiii_xmldir = "ZONEXML/"

#segmentation_cmd = "./rast-ocropus"
#segmentation_algorithm = "rast"

segmentation_cmd = "./voronoi-ocropus"
segmentation_algorithm = "vor"

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


def get_document_id_from_basename( basename ) :
    # split the basename (e.g., ("A00BZONE_300_010_0000_rast") into just the
    # UW-III document ID
    fields = basename.split("_")
    document_id = fields[0]
    return document_id

running_filename = None

def handler( signum, frame ) : 
    print running_filename
    result = subprocess.check_output( "ps waux | grep "+running_filename, shell=True )
    print result

    fields = result.split()
    pid = int(fields[1])

    print "killing pid=",pid 

    os.kill(pid,signal.SIGKILL )

def run_image_with_gtruth( imgfilename, gtruth_xml_filename ) :
    basename = get_basename(imgfilename)

    document_id = get_document_id_from_basename( basename )
    out_imgfilename = output_dir + "{0}_{1}.png".format( 
                        basename, segmentation_algorithm )
    xml_filename = output_dir + "{0}_{1}.xml".format( 
                        basename, segmentation_algorithm ) 

    # inputs
#    print "imgfilename=",imgfilename
#    print "gtruth_xml_filename=",gtruth_xml_filename

    # outputs
#    print "xml_filename=",xml_filename
#    print "out_imgfilename=",out_imgfilename
#    sys.exit(0)

    # segment the image
    cmd = "{0} {1} {2}".format( segmentation_cmd, imgfilename, out_imgfilename ) 
#    cmd = "./rast-ocropus {0} {1}".format( imgfilename, out_imgfilename ) 

    signal.signal( signal.SIGALRM, handler )
    # small optimization; if the result already exists, don't run it again
    # (crash recovery)
    print cmd
    if os.path.exists( xml_filename ) :
        print "{0} already exists so assume seg already run".format( xml_filename )
    else : 
        global running_filename 
        running_filename = imgfilename 

        signal.alarm( 5 )
        try : 
            result = subprocess.check_output( cmd.split() )
            signal.alarm(0)
        except subprocess.CalledProcessError : 
            signal.alarm(0)
            return { "output_image_file": out_imgfilename, 
                     "output_xml_file": "failed",
                     "metric" : 0 } 

        # write the XML results 
        with open(xml_filename,"w") as outfile :
            print >>outfile, result
        print "wrote", xml_filename

    # run the compare
    cmd = "./runZoneComp -g {0} -d {1}".format( gtruth_xml_filename, xml_filename )
    print cmd

    try : 
        result = subprocess.check_output( cmd.split() )
    except subprocess.CalledProcessError : 
        return { "output_image_file": out_imgfilename, 
                 "output_xml_file": "failed",
                 "metric" : 0 } 

    # get the segmentation metric from the output
    metric = parse_runZoneComp_result( result ) 
    print "metric={0}".format( metric )

    return { "output_image_file": out_imgfilename, 
             "output_xml_file": xml_filename,
             "metric" : metric } 

def run_all_uwiii( ) :
    # run all UW-III images
    global output_dir
    output_dir = "fullpage/"

    result_list = []
    for imgfilename in sys.argv[1:] :
        basename = get_basename(imgfilename)
        document_id = get_document_id_from_basename( basename )

        # zone box files use "ZONE" instead of "BIN"
        # e.g., 
        # A00ABIN_300_010_2990.png -> A00AZONE_300_010_2990.xml 
        gtruth_xml_filename = uwiii_xmldir + "{0}.xml".format( basename.replace("BIN","ZONE") )

#        print basename, document_id, gtruth_xml_filename

        result = run_image_with_gtruth( imgfilename, gtruth_xml_filename )
        result_list.append( result ) 

        # save pickled file so can do interesting things with the results later
        # (especially if we crash)
        output = open( "uwiii.pkl", "wb" )
        pickle.dump(result_list,output)
        output.close()

        xmlfilename = result["output_xml_file"]

        # did we crash? if so don't bother trying to draw the XML
        if xmlfilename == "failed" : 
            print "{0} failed!".format( imgfilename )
            continue
        
        # draw the resulting XML onto the original input image
        out_imgfilename = output_dir + "{0}_zones.png".format(document_id)

        if os.path.exists( out_imgfilename ) : 
            print "{0} already exists; not redrawing".format( out_imgfilename ) 
            continue

        drawxml.draw_zones( xmlfilename, imgfilename, out_imgfilename )
        print "wrote", out_imgfilename

    outfile = open("uwiii.dat","w")
    for result in result_list : 
        print >>outfile, "{0} {1} {2}".format(
            result["output_image_file"],
            result["output_xml_file"],
            result["metric"] )
    outfile.close()

def run_file_list( img_filelist, xml_filelist, output_basename ) :

    result_list = []

    pickle_filename = output_dir + output_basename + ".pkl"
    dat_filename = output_dir + output_basename + ".dat"

    for imgfilename,gtruth_xml_filename in zip(img_filelist, xml_filelist) :
        basename = get_basename(imgfilename)
        document_id = get_document_id_from_basename( basename )

        result = run_image_with_gtruth( imgfilename, gtruth_xml_filename )
        result_list.append( result ) 

        # save pickled file so can do interesting things with the results later
        # (especially if we crash)

        output = open( pickle_filename, "wb" )
        pickle.dump(result_list,output)
        output.close()

        xmlfilename = result["output_xml_file"]

        # did we crash? if so don't bother trying to draw the XML
        if xmlfilename == "failed" : 
            print "{0} failed!".format( imgfilename )
            continue
        
        # draw the resulting XML onto the original input image
        out_imgfilename = output_dir + "{0}_zones.png".format(basename)

        if os.path.exists( out_imgfilename ) : 
            print "{0} already exists; not redrawing".format( out_imgfilename ) 
            continue

        drawxml.draw_zones( xmlfilename, imgfilename, out_imgfilename )
        print "wrote", out_imgfilename

    outfile = open(dat_filename,"w")
    for result in result_list : 
        print >>outfile, "{0} {1} {2}".format(
            result["output_image_file"],
            result["output_xml_file"],
            result["metric"] )
    outfile.close()

def sanity_check_images( document_id ) : 
    img_file_list,xml_file_list = get_file_lists( document_id )

    for imgfilename,xmlfilename in zip(img_file_list,xml_file_list) : 
        basename = get_basename(imgfilename)
        document_id = get_document_id_from_basename( basename )

        print imgfilename, xmlfilename, document_id

        img = Image.open(imgfilename)
        img.load()
        xmlfile = open(xmlfilename,"r")
        xmlfile.close()
        del img

def get_file_lists( document_id ) : 
    # load all input images and their XML ground truth
    input_dir = str(num_rows) + "/" + document_id + "/"

    img_file_list = glob.glob( input_dir + "/*.png" ) 

    xml_file_list = [ s.replace(".png",".xml") for s in img_file_list ]

    return img_file_list, xml_file_list

def run_image( document_id ) : 

#    # sanity check before we begin the day's festivities
#    sanity_check_images( document_id )
    
    img_file_list,xml_file_list = get_file_lists( document_id )

    global output_dir

    output_dir = "{0}_{1}/{2}/".format( 
                    num_rows, segmentation_algorithm, document_id )

    if not os.path.exists(output_dir) :
        os.mkdir(output_dir)

    run_file_list( img_file_list, xml_file_list, document_id )

def run_dir( dirname ) : 
    img_dir_list = glob.glob(dirname) 
    print img_dir_list

    count = 0
    for dirname in img_dir_list : 
        count += 1
        # get the document id
        document_id = dirname.split("/")[-1]
        run_image( document_id )

        print "{0} of {1}".format( count, len(img_dir_list) )

def parse_args() :
    helptext = "Specify either docid OR image+gtruth"

    parser = argparse.ArgumentParser( description="Run page segmentation" )

    parser.add_argument( "--seg", help="segmentation algorithm to run (default==rast)",
                         default="rast", choices=("rast","voronoi",) )
    parser.add_argument( "--docid", help="document ID to segment" )
    parser.add_argument( "--image", help="source image to segment" )
    parser.add_argument( "--gtruth", help="ground truth XML" )

    args = vars( parser.parse_args() )

    print args

    # sanity check some mutual exclusion arguments
    if args["docid"] : 
        if args["image"] or args["gtruth"] : 
            err = "Error: must specify either docid OR image+gtruth\n"
            parser.exit(-1,err)
    else : 
        if not ( args["image"] and args["gtruth"] ) : 
            err = "Error: must specify both image and groundtruth files\n"
            parser.exit(-1,err)

    return args

def main() :
    args = parse_args() 

    global segmentation_cmd
    global segmentation_algorithm
    if args["seg"]=="rast" : 
        segmentation_cmd = "./rast-ocropus"
        segmentation_algorithm = "rast"
    elif args["seg"] == "voronoi" :
        segmentation_cmd = "./voronoi-ocropus"
        segmentation_algorithm = "vor"
    else : 
        raise Exception("Unknown segmentation algorithm "+args[seg] )
        
    if args["docid"] :
        document_id = args["docid"]
        run_image( document_id ) 

    elif args["image"] : 
        imgfilename = args["image"]
        xmlfilename = args["gtruth"]

        run_image_with_gtruth( imgfilename, xmlfilename ) 

if __name__=='__main__':
#    run_all_uwiii()
    main()
#    run_image( sys.argv[1] )
#    sanity_check_images( sys.argv[1] )
#    run_dir("{0}/*".format(num_rows))

    
