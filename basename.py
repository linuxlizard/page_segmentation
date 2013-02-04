#!python

import os

def get_basename( filename ) : 
    return os.path.splitext( os.path.split( filename )[1] )[0]

