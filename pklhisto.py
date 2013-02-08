#!/usr/bin/python

# Load ocropus output metric pickle files
# davep 07-Feb-2013

import sys
import pickle
import numpy as np
import matplotlib.pyplot as plt

def load_pickle( pickle_name ) :
    f = open(pickle_name,"rb")
    data = pickle.load(f)
    f.close()

    # convert to numpy array and return
    metric = [ d["metric"] for d in data ]
    return np.asarray( metric, dtype="float" )

def main() : 
    metrics = np.empty(shape=(1,),dtype="float")
    for pickle_name in sys.argv[1:] : 
        ndata = load_pickle( pickle_name ) 
#        print ndata
        metrics = np.append( metrics, ndata )

    print metrics.shape

    adjmetrics = np.nan_to_num(metrics)

    nonzero = np.where( adjmetrics != 0 )

    plt.hist( adjmetrics[nonzero], bins=100 )
    plt.show()

if __name__=='__main__':
    main()

