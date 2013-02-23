#!python

import numpy as np
import itertools

import datfile

def print_latex_table( outfilename, output_list ) :
    prefix ="""
    \\begin{tabular}{| l | l | l | l | }
    \\hline
    Name    &   Total Metrics & Zeros & \\% Non Zero \\\\
    \\hline"""

    data = """
    {name} & {count} & {zeros} & {percent:.2f} \\\\
    \\hline"""

    postfix = """
    \\end{tabular}"""

    outfile = open(outfilename,"w")
    print >>outfile, prefix,

    for s in output_list : 
#        print >>outfile, data.format( file["name"], file["size"], file["new_size"])
#        print >>outfile, data.format( s["name"], s["count"], s["zeros"], s["percent"] )
        print s["name"]
        print >>outfile, data.format(**s)
    
    print >>outfile, postfix


def count_zeros(dataset,algorithm,stripsize) : 

    metrics = datfile.load_metrics(dataset=dataset,algorithm=algorithm,stripsize=stripsize )

#    zeros = np.where(metrics==0)

    num_nonzero = np.count_nonzero(metrics)
    num_elements = len(metrics)

#    print name, num_elements, num_nonzero

#    print "num_nonzero=",num_nonzero
#    print "num_elements=",len(metrics)

    return (num_nonzero, num_elements, float(num_nonzero)/float(num_elements) )

def calculate_all_zeros() : 
#    count_zeros("uwiii","rast","fullpage")
        
    table = []
    itr = itertools.product(datfile.dataset_list,datfile.algorithm_list,datfile.stripsize_list)
    for i in itr : 
        name = " ".join(i)
        zero_info  = count_zeros(i[0],i[1],i[2])
        table.append( { "name":name,
                        "count": zero_info[1]+zero_info[0],
                        "zeros": zero_info[1]-zero_info[0],
                        "percent": zero_info[2]} )

    print_latex_table( "zeros_table.tex", table )

def calculate_total_performance(algo) : 

    winder_metrics = datfile.load_metrics( dataset="winder", stripsize="300", 
                                    algorithm=algo )
    uwiii_metrics = datfile.load_metrics( dataset="uwiii", stripsize="300",
                                    algorithm=algo )

    print winder_metrics.shape
    print uwiii_metrics.shape

    all_300 = np.concatenate((winder_metrics, uwiii_metrics))

    print "all {0} len={1}".format( algo, len(all_300) )
    print "all {0} mean={1}".format( algo,  np.mean(all_300) )
    print "all {0} stddev={1}".format( algo,  np.std(all_300) )

    nz = np.nonzero(all_300)
    print len(all_300[nz])
    print "all {0} numzeros={1}".format( algo,  len(all_300)-len(all_300[nz]))

def count_uwiii_zeros() : 
    metrics = datfile.load_metrics( dataset="uwiii", stripsize="300",
                                          algorithm="rast")
    
    num_nonzero = np.count_nonzero(metrics)
    num_elements = len(metrics)

    print num_elements, num_nonzero
    print "num_nonzero=",num_nonzero
    print "num_elements=",num_elements
    print "num_zero=",num_elements-num_nonzero

def main() : 
#    calculate_all_zeros()

    count_uwiii_zeros()

#    calculate_total_performance("rast") 
#    calculate_total_performance("vor") 
#    calculate_total_performance("fullpage") 

if __name__=='__main__':
    main()

