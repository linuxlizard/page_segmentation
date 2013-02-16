#!/usr/bin/python

# sweep through images in Amy Winder's image set and runseg.py on each
# davep 09-Feb-2013

import sys
import os
import os.path
import glob
import Image
import pickle

import runseg
from basename import get_basename

num_rows=600

#root = "imagesAndgTruth"
#root = "300_winder/imagesAndgTruth"
root = "600_winder/imagesAndgTruth"

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
        if ".DS_Store" in rdir: 
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

        print img_filelist
        print xml_filelist

        s = "{0}_winder_{1}".format(numrows,runseg.segmentation_algorithm)
        output_dir = os.path.join(s,rdir,"300dpi")
#        output_dir = os.path.join("300_winder_fullpage_rast",rdir,"300dpi")
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        output_basename = rdir
#        runseg.run_file_list( img_filelist, xml_filelist, output_dir, output_basename )


def foo() :
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

def load_image_and_xml_list( dirname ) :
    # sweep a dir; load the list of .png and corresponding ground truth .xml
    # files. Store in a .pkl as cache

    pklfilename = dirname+".pkl"

    test = 0

    if os.path.exists(pklfilename) : 
        pfile=open(pklfilename,"rb")
        img_filelist,xml_filelist = pickle.load(pfile)
        pfile.close()
        print "loaded from pickle"
        return img_filelist,xml_filelist

    img_filelist = []
    xml_filelist = []

    for root,dirs,files in os.walk(dirname) :
        for f in files : 
            path=os.path.join(root,f)
            if path.endswith(".png") : 
                imgfilename = path
                basename = get_basename(imgfilename)

                if test : 
                    img = Image.open(path)
                    img.load()
                    del img

                # look for the xmlfile
                xmlfilename = path.replace(".png",".xml")

                if test: 
                    f = open(xmlfilename,"r")
                    f.close()

                print imgfilename, xmlfilename
                img_filelist.append( imgfilename )
                xml_filelist.append( xmlfilename )
    
    pfile = open(pklfilename,"wb")
    pickle.dump((img_filelist,xml_filelist),pfile)
    pfile.close()
    
    return img_filelist,xml_filelist

def main_2() :
    def make_outdir(img_filename) :
        # split a png filename into an appropriate output path
        pathname,filename = os.path.split(img_filename)
#        print pathname
#        print filename
        dirlist = pathname.split(os.sep)
#        print dirlist, dirlist[1:]
        outdir = os.path.join(*dirlist[1:])
#        print outdir
        return outdir

    output_dir_base = "600_winder_{0}".format(runseg.segmentation_algorithm)
    input_dirname = "600_winder"

    img_filelist, xml_filelist = load_image_and_xml_list( input_dirname )

    output_dir_hash = {}
    for i,x in zip(img_filelist,xml_filelist) : 
        od = make_outdir(i)
        if not od in output_dir_hash : 
            output_dir_hash[od] = []

        output_dir_hash[od].append( get_basename(i) )

    pklname = "{0}_output_dir_hash.pkl".format(input_dirname)
    f = open( pklname, "wb" )
    pickle.dump(output_dir_hash,f)
    f.close()
#    print "wrote",pklname

#    fname_fmt = "{0}_{1}".format( input_dirname
    for dirname in output_dir_hash.keys() : 

        filelist = [ os.path.join(input_dirname,dirname,f) for f in
                            output_dir_hash[dirname] ]
        img_filelist = [ s+".png" for s in filelist ] 
        xml_filelist = [ s+".xml" for s in filelist ] 

        output_basename = os.path.split(dirname)[-1]
        print img_filelist[0]
        print xml_filelist[0]

        output_dir = os.path.join(output_dir_base,dirname)
        print "outputdir=",output_dir
        print output_basename

        if not os.path.exists(output_dir) :
            os.makedirs(output_dir)

        runseg.run_file_list( img_filelist, xml_filelist, output_dir, output_basename )

        sys.exit(0)

if __name__=='__main__' : 
#    main()
    main_2()

