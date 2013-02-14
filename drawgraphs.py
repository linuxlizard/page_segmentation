#!/usr/bin/python

# Load ocropus output metric dat files. Draw many delightful graphs.
#
# davep 09-Feb-2013

import os
import sys
import csv
import numpy as np
#import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg

from basename import get_basename
import datfile

def make_histogram( metrics, outfilename, **kargs ) : 
    
    adjmetrics = np.nan_to_num(metrics)
    nonzero = np.where( adjmetrics != 0 )

#    foo = plt.hist( adjmetrics[nonzero], bins=100, normed=True )
#    plt.show()

    fig = Figure()

    if "title" in kargs : 
        fig.suptitle(kargs["title"])

    ax = fig.add_subplot(111)
    ax.grid()
    ax.hist(np.nan_to_num(metrics),bins=25,normed=True)

    canvas = FigureCanvasAgg(fig)
    canvas.print_figure(outfilename)
    print "wrote", outfilename

def load_all_datfiles( dirname ) : 
    metrics = None

    for root,dirs,files in os.walk(dirname) :
#        print "root=",root
#        print "dirs=",dirs
#        print "files=",files
        for f in files : 
            path=os.path.join(root,f)
            if path.endswith(".dat") : 
#                print "path=",os.path.join(root,f)
                ndata = datfile.load( path )
#                print ndata

                if metrics is None : 
                    metrics = ndata
                    ndata = None
                else :
                    metrics = np.append( metrics, ndata )

    return metrics

def plotit( data, outfilename, **kargs ) :

    # going to make a 1 row x N column plot
    if len(data.shape)==1 : 
        num_rows = 1
    else : 
        num_rows = data.shape[1]

    # davep 02-Oct-2012 ; bump up the size to accommodate multiple rows
    fig = Figure()
    figsize = fig.get_size_inches()
#    fig.set_size_inches( (figsize[0],figsize[1]*num_rows) )

    if "title" in kargs : 
        fig.suptitle(kargs["title"])

    # http://matplotlib.org/faq/howto_faq.html
    # "Move the edge of an axes to make room for tick labels"
    # hspace is "the amount of height reserved for white space between
    # subplots"
    fig.subplots_adjust( hspace=0.40 )

    ax = fig.add_subplot(111)
    ax.grid()
    for i in range(num_rows) : 
        if num_rows==1 :
            column = data 
        else : 
            column = data[ :, i ] 

        fmt = kargs.get("fmt","+")
        if "color" in kargs : 
            fmt += kargs["color"]            
        ax.plot(column,fmt)

    if "axis_title" in kargs : 
        title = kargs["axis_title"][i]
        ax.set_title(title)

    canvas = FigureCanvasAgg(fig)
    canvas.print_figure(outfilename)
    print "wrote", outfilename

def draw_single_pages() : 
    def make_lines(ndata,fullpage_metric) :
        # make horizontal data sets for metric and mean
        fullpage = np.ones_like(ndata) * fullpage_metric
        m = np.ones_like(ndata) * np.mean(ndata)
        print "mean=",np.mean(ndata)
        return np.column_stack((ndata,fullpage,m))

    base = "300_winder_rast/imagesAndgTruth/"
    # draw a few results from single pages
    outfilename = "winder_full_rast_double_2col300_1.eps"
    if not os.path.exists(outfilename): 
        ndata = datfile.load(base+"Double_Column/300dpi/2col300_1/2col300_1.dat")
        plotit( make_lines(ndata,1.0),
                    outfilename, title="Winder RAST DoubleColumn 2col300_1", fmt="-" )

    outfilename = "winder_full_rast_double_pic_2col300_2.eps"
    if not os.path.exists(outfilename): 
        ndata = datfile.load(base+"Double_Column_Pictures/300dpi/2colpic300_2/2colpic300_2.dat")
        plotit( make_lines(ndata,.78), outfilename, 
                title="Winder RAST Double Column Picture 2col300_2", 
                fmt="-" )

    outfilename = "winder_full_rast_double_sci_2col300_3.eps"
    if not os.path.exists(outfilename): 
        ndata = datfile.load(base+"Double_Column_Pictures_Scientific/300dpi/2colpic300_3/2colpic300_3.dat")
        plotit( make_lines(ndata,.56), outfilename, 
                title="Winder RAST Double Column Scientific Picture 2col300_3", 
                fmt="-" )

def get_winder_class_results(class_dir) :
    # load all .dat files corresponding to each class of image in the Winder
    # data set

    # gather all the datafiles from the fullpage winder
    fullpage_winder = datfile.find_all(class_dir)

    class_means = []
    class_names = []
    for datfilename in fullpage_winder : 
        print datfilename

        ndata = datfile.load(datfilename)
        basename = get_basename(datfilename)
        print basename, np.mean(ndata)
        class_means.append( np.mean(ndata) )
        class_names.append( basename.replace( "_"," ") )

    return (class_means,class_names)

def draw_winder_class_results() : 

    rast_means, rast_names = get_winder_class_results( "300_winder_fullpage_rast" )
    vor_means, vor_names = get_winder_class_results( "300_winder_fullpage_vor" )

    print zip(rast_means, rast_names)
    print zip(vor_means, vor_names)

    # http://matplotlib.org/examples/api/barchart_demo.html
    fig = Figure()
    ax = fig.add_subplot(111)
#    fig.subplots_adjust( hspace=0.90 )

    ind = np.arange(len(rast_means))
    width = 0.35

    rects1 = ax.bar( ind, rast_means, width, color='r' )
    rects2 = ax.bar( ind+width, vor_means, width, color='g' )
    ax.set_xticklabels( vor_names, rotation='vertical' )
    ax.legend( (rects1[0],rects2[0]),('RAST','Vor'))

    outfilename = "winder_class_rast_vs_vor.eps"
    canvas = FigureCanvasAgg(fig)
    canvas.print_figure(outfilename)
    print "wrote", outfilename


def graph_all_results() : 
    result_list = [ 
        { "dir" :   "300_winder_fullpage_rast",
          "outfile": "winder_fullpage_rast.eps",
          "title" : "Winder Full Page RAST" },
        { "dir" :   "300_winder_fullpage_vor",
          "outfile": "winder_fullpage_vor.eps",
          "title" : "Winder Full Page Voronoi" },

        { "dir" :   "300_winder_rast",
          "outfile": "300_winder_rast.eps",
          "title" : "Winder 300 RAST" },

        { "dir" :   "300_winder_rast",
          "outfile": "300_winder_rast.eps",
          "title" : "Winder 300 RAST" },
        { "dir" :   "300_winder_vor",
          "outfile": "300_winder_vor.eps",
          "title" : "Winder 300 Voronoi" },

        { "dir" :   "300_vor",
          "outfile": "300_uwiii_vor.eps",
          "title" : "UW-III 300 Voronoi" },
        { "dir" :   "300_rast",
          "outfile": "300_uwiii_rast.eps",
          "title" : "UW-III 300 RAST" },
    ]

    # add each image class of Amy Winder's data set
    awinder_class_list = ( 
        "Double_Column",
        "Magazine",
        "Single_Column",
        "Double_Column_Pictures",
        "Mixed_Columns",
        "Single_Column_Pictures",
        "Double_Column_Pictures_Scientific",
        "Mixed_Columns_Pictures" )
    for c in awinder_class_list : 
        result_list.append({"dir": os.path.join("300_winder_fullpage_rast", c),
                            "outfile" : "awinder_"+c+"_rast.eps",
                            "title": "Winder " + c.replace("_"," " ) + " RAST"})
    for c in awinder_class_list : 
        result_list.append({"dir": os.path.join("300_winder_fullpage_vor", c),
                            "outfile" : "awinder_"+c+"_vor.eps",
                            "title": "Winder " + c.replace("_"," " ) + " Voronoi"})

    for result in result_list : 
        if not os.path.exists( result["outfile"] ) :
            print result["dir"]
            ndata = load_all_datfiles(result["dir"]) 
            np.save('metrics.npy',ndata)
            make_histogram( ndata, result["outfile"], title=result["title"] )

    if not os.path.exists("uwiii_full_page.eps") :
        ndata = np.loadtxt( "fullpage_metric.dat" )
        print ndata
        make_histogram( ndata, "uwiii_full_page.eps", title="UW-III Full Page RAST" )

    # draw a few single page graphs
    draw_single_pages()

    # draw a graph of each class of the winder dataset
    draw_winder_class_results()
    
#    ndata = load_all_datfiles( "300_winder_fullpage_vor" ) 
#    make_histogram( ndata, "300_winder_fullpage_vor.eps", title="300 Winder Fullpage Voronoi" )

def usage() : 
    print >>sys.stderr, "usage: drawgraphs [list of datfiles]"

def main() : 
    if len(sys.argv) < 2 : 
        usage()
        return

    metrics = None

    for datfile_name in sys.argv[1:] : 
        print datfile_name
        ndata = datfile.load( datfile_name ) 
#        print ndata
        if metrics is None : 
            metrics = ndata
            ndata = None
        else :
            metrics = np.append( metrics, ndata )
        print metrics

    print metrics.shape

    np.save('metrics.npy',metrics)
    make_histogram( metrics, "out.png" ) 

if __name__=='__main__':
#    main()
    graph_all_results()

