#!/usr/bin/python

# sweep through images in Amy Winder's image set and runseg.py on each
# davep 09-Feb-2013

import sys
import os
import os.path
import glob
import Image

import runseg
from basename import get_basename

root = "imagesAndgTruth"
#root = "300_winder/imagesAndgTruth"

#runseg.segmentation_cmd = "./rast-ocropus"
#runseg.segmentation_algorithm = "rast"
runseg.segmentation_cmd = "./voronoi-ocropus"
runseg.segmentation_algorithm = "vor"

def main() : 
    root_dirs = os.listdir(root)

    for rdir in root_dirs : 
        # skip the subversion directories
        if ".svn" in rdir: 
            continue

        print "dir=",rdir

        # only do the 300dpi images for now
        image_dirs = os.listdir( os.path.join( root, rdir, "300dpi" ) )

        print "image_dirs=",image_dirs

        assert "png" in image_dirs 

        image_dirs = [ d for d in image_dirs if ".svn" not in d ]
        print "image_dirs=",image_dirs

        assert ".svn" not in rdir, rdir

        png_path = os.path.join(root,rdir,"300dpi","png")
        print "png_path=",png_path

        img_filelist = glob.glob(os.path.join(png_path,"*.png"))
        print "img_filelist=",img_filelist
        assert len(img_filelist)

        xml_filelist = [] 

        for imgfile in img_filelist :
            fields = os.path.split(imgfile)
            print fields
            xmlfile = os.path.join( fields[0].replace("png","gTruth"), 
                                    fields[1].replace(".png",".xml") )

            print "imgfile=",imgfile,"xml_file=",xmlfile
            img = Image.open(imgfile)
            img.load()
            try : 
                f = open(xmlfile,"r")
                f.close()
            except IOError,e :
                if e.errno==2 :
                    # try our luck with the gTruth/xml dir
                    xmlfile = os.path.join( fields[0].replace("png","gTruth"), 
                                            "xml",
                                            fields[1].replace(".png",".xml") )
                    f = open(xmlfile,"r")
                    f.close()
                else : 
                    raise

            xml_filelist.append( xmlfile )

        output_dir = os.path.join("300_winder_fullpage_vor",rdir,"300dpi")
#        output_dir = os.path.join("300_winder_fullpage_rast",rdir,"300dpi")
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        output_basename = rdir
        runseg.run_file_list( img_filelist, xml_filelist, output_dir, output_basename )

        continue

        for imgdir in image_dirs : 
            print "imgdir=",imgdir
            # did we land in a dir with png files? 
            if "png" not in imgdir : 
                continue

            print root,rdir,imgdir
            imgpath = os.path.join(root,rdir,"300dpi",imgdir)
            print "imgpath=",imgpath

            # subversion metadata keeps messing with me
            assert ".svn" not in rdir, rdir
            assert ".svn" not in imgdir, imgdir
            assert ".svn" not in root, root
            assert ".svn" not in imgpath, imgpath

            # did we land in a dir with png files? 
            pngfiles = glob.glob(os.path.join(imgpath,"*.png"))
            assert len(pngfiles)

            # write the results to a path different than the source
            output_dir = os.path.join(imgpath)
#            output_dir = output_dir.replace( "300_winder/", "300_winder_vor/" )
#            output_dir = output_dir.replace( "300_winder/", "300_winder_rast/" )
#            output_dir = os.path.join( "300_winder_fullpage_vor", output_dir )
            output_dir = os.path.join( "300_winder_fullpage_rast", output_dir )

            # destination doesn't exist, make it
            if not os.path.exists(output_dir) : 
                os.makedirs( output_dir )

            img_filelist = pngfiles
            xml_filelist = [ s.replace(".png",".xml") for s in img_filelist ]

            # output data file name is based on the last dir in the tree
#            print "imgpath=",imgpath
            output_basename = os.path.split(imgpath)[-1]
            
#            print "output_dir=",output_dir
#            print "output_basename=",output_basename

            runseg.run_file_list( img_filelist, xml_filelist, output_dir, output_basename )

if __name__=='__main__' : 
    main()

