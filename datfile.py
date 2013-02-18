#!python

# Load a .dat file which is our output of runseg.py
# Moved into own module so can call from oodles of other python scripts.
#
# davep 13-Feb-2013

import sys
import os
import numpy as np
import csv
import pickle
import sqlite3

from basename import get_basename

def load( datfile_name ) :
    
    infile = open(datfile_name,"r")
    reader = csv.reader( infile, delimiter=' ')
    data = [ float(row[2]) for row in reader ] 
    infile.close()

    return np.nan_to_num(np.asarray( data, dtype="float" ))

def find_all( dirname ) : 
    # sweep a path (like 'find') and gather all .dat filenames
    datfile_list = []
    for root,dirs,files in os.walk(dirname) :
#        print "root=",root
#        print "dirs=",dirs
#        print "files=",files
        for f in files : 
            path=os.path.join(root,f)
            if path.endswith(".dat") : 
                datfile_list.append( path ) 

    return datfile_list

def load_all_data(root) : 
    fullpage_winder = find_all(root)

    data_list = []
    path_list = []
    for datfilename in fullpage_winder : 
        ndata = load(datfilename)
        data_list.append( ndata )
        # detach ref
        ndata = None

        path_list.append( datfilename)

    return path_list, data_list

def load_results_tree( results_hash ) : 
    for root in results_hash.keys() :
        print root
        names, data = load_all_data(root)
        results_hash[root] = {"names":names,"data":data}

    return results_hash

def load_all_results() :
    pklname = "winder_results.pkl" 
    if os.path.exists(pklname):
        with open(pklname,"rb") as f : 
            winder_results = pickle.load(f)
        print "loaded",pklname
    else : 
        winder_results = { "winder_fullpage_rast" : None,
                           "winder_fullpage_vor" : None,
                           "300_winder_rast" : None,
                           "600_winder_rast" : None,
                           "300_winder_vor" : None,
                           "600_winder_vor" : None }
        winder_results = load_results_tree( winder_results )
        with open(pklname,"wb") as f : 
            pickle.dump(winder_results,f)
            print "wrote", pklname 

    pklname = "uwiii_results.pkl"
    if os.path.exists(pklname) :
        with open(pklname,"rb") as f : 
            uwiii_results = pickle.load(f)
        print "loaded",pklname
    else : 
        uwiii_results = { #"fullpage_rast" : None,
                          #"fullpage_vor" : None,
                          "300_rast" : None,
                          "600_rast" : None,
                          "300_vor" : None,
                          "600_vor" : None }
        uwiii_results = load_results_tree( uwiii_results )
        with open(pklname,"wb") as f : 
            pickle.dump(uwiii_results,f)

#    uwiii_fullpage_rast = load(os.path.join("uwiii_fullpage","uwiii_fullpage_rast.dat"))
#    uwiii_fullpage_vor = load(os.path.join("uwiii_fullpage","uwiii_fullpage_vor.dat"))


#    print uwiii_fullpage_rast
#    print uwiii_fullpage_vor
    
    return winder_results, uwiii_results

db_fields_list = ( "filename" ,
              "algorithm" ,
              "stripsize" ,
              "dataset" ,
              "class" ,
              "metrics"  )

# empty hash with fields that become the fields in our DB
db_fields = dict( [ (k,None) for k in db_fields_list] )
#db_fields = { "filename" : None,
#              "algorithm" : None,
#              "stripsize" : None,
#              "dataset" : None,
#              "class" : None,
#              "metrics" : None }

valid_stripsizes = ( "300", "600", "fullpage" )

def decode_winder_filename(filename) : 
    # split a winder .dat filename into necessary components

    valid_classnames = (
        "Double_Column",
        "Mixed_Columns",
        "Double_Column_Pictures",
        "Mixed_Columns_Pictures",
        "Double_Column_Pictures_Scientific",
        "Single_Column",
        "Magazine",
        "Single_Column_Pictures"
    )

#    fields = { "filename" : None,
#           "algorithm" : None,
#           "stripsize" : None,
#           "dataset" : None,
#           "class" : None }
    fields = dict(db_fields)
    fields["dataset"] = "winder"

    # e.g., 
    # 600_winder_rast/imagesAndgTruth/Double_Column/300dpi/2col300_1/2col300_1.dat
    # winder_fullpage_rast/Double_Column/300dpi/Double_Column.dat

    fields["filename"] = filename

    # get the class name from the dirname
    dirnames = filename.split(os.sep)

    # the results are in directory trees with two different styles
    if "imagesAndgTruth" in filename : 
        fields["class"] = dirnames[2]
        fields["stripsize"],owner,fields["algorithm"]= dirnames[0].split("_")
    else : 
        fields["class"] = dirnames[1]
        fields["stripsize"] = "fullpage"
        x,x,fields["algorithm"]= dirnames[0].split("_")
        
    assert fields["class"] in valid_classnames, fields["class"]
    assert fields["stripsize"] in valid_stripsizes, fields["stripsize"]

    return fields

def decode_uwiii_filename( filename ) : 
    fields = dict(db_fields)
    fields["dataset"] = "uwiii"

    dirnames = filename.split(os.sep)
    
    fields["filename"] = filename
    fields["stripsize"],fields["algorithm"]= dirnames[0].split("_")

    assert fields["stripsize"] in valid_stripsizes, fields["stripsize"]

    # classname is the first letter of the data directory name
    # e.g., "A001ZONE" is the 'A' dataset
    fields["class"] = dirnames[-1][0]

    return fields

def store_result_data_to_db( cur, results ) : 
    for k in results.keys() : 
        name_list = results[k]["names"]
        data_list = results[k]["data"]
        for name,data in zip(name_list,data_list) : 
#            f = decode_winder_filename( name )
            if "winder" in name : 
                f = decode_winder_filename( name )
            else : 
                f = decode_uwiii_filename( name ) 
#            print f
            cur.execute( "INSERT INTO pageseg VALUES(?,?,?,?,?,?)",
                (f["filename"],f["algorithm"],f["stripsize"],
                 f["dataset"],f["class"],data.tostring()))

def save_to_sqlite() : 
    winder_results, uwiii_results = load_all_results()
    
#    pklname = "winder_results.pkl" 
#    with open(pklname,"rb") as f : 
#        winder_results = pickle.load(f)
#    print "loaded",pklname

    conn = sqlite3.connect("pageseg.db")
    conn.text_factory = str
    cur = conn.cursor()

    cur.execute( "DROP TABLE pageseg" )

    creat = """
CREATE TABLE IF NOT EXISTS pageseg
    (filename text,
     algorithm text,
     stripsize text,
     dataset text,
     class text, 
     metrics text)
"""
    cur.execute( creat )

    store_result_data_to_db( cur, winder_results )
    store_result_data_to_db( cur, uwiii_results )

    # my UW-III fullpage rast and voronoi are in separate datafiles
    # I ran them on multiple machines, splitting the jobs by class and by
    # algorithm.
    # The datafile contains lines like:
    # fullpage_vor/A001BIN_vor.png fullpage_vor/A001BIN_vor.xml 0.0
    file_list = ( "uwiii_fullpage_rast.dat", "uwiii_fullpage_vor.dat" )
    for filename in [ os.path.join("uwiii_fullpage",f) for f in file_list ] : 
        # read all lines from the file into an array 
        with open( filename, "r" ) as infile : 
            lines = [ l.strip() for l in infile.readlines() ]

        # parse the data into a dict we will put into the DB
        for l in lines : 
            # line should look like:
            # fullpage_vor/A001BIN_vor.png fullpage_vor/A001BIN_vor.xml 0.0

            # split into space separated fields
            fields = l.split()

            # metric is the last field
            data = np.array( fields[-1], dtype="float" )

            # get the png filename; we'll use it to split into filename and
            # algorithm
            basename = get_basename(fields[0])
            filename,algorithm = basename.split("_")

            f = dict(db_fields)
            f["filename"] = filename
            f["algorithm"] = algorithm
            f["stripsize"] = "fullpage"
            f["dataset"] = "uwiii"
            # first letter of the base e.g., W1U8BIN_vor
            f["class"] = basename[0] 

            cur.execute( "INSERT INTO pageseg VALUES(?,?,?,?,?,?)",
                (f["filename"],f["algorithm"],f["stripsize"],
                 f["dataset"],f["class"],data.tostring()))

    conn.commit()
    conn.close()

def test_db() : 
    conn = sqlite3.connect("pageseg.db")
    conn.text_factory = str
    cur = conn.cursor()

    # run a quick test to make sure we can get the numpy data back out
    cur.execute('SELECT * FROM pageseg WHERE dataset="winder" and algorithm="rast" and stripsize="fullpage"')
#    cur.execute('SELECT * FROM pageseg WHERE dataset="winder" and algorithm="rast" and stripsize="600"')
#    cur.execute('SELECT * FROM pageseg WHERE dataset="winder" and algorithm="rast" and stripsize="300"')
    rows = cur.fetchall()
    for r in rows : 
        datarow = dict(zip(db_fields_list,r))
        print datarow["filename"]
#        print r[5]
#        data = np.fromstring(r[5],dtype="float")
        data = np.fromstring(datarow["metrics"],dtype="float")
        if len(data)==0 : 
            print "failed?", datarow["filename"]
        else : 
            print data.shape,data.mean(),np.min(data),np.max(data)

    conn.close()

if __name__=='__main__':
#    load_all_results()
    save_to_sqlite()
#    test_db()

