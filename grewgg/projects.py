
from __future__ import print_function

"""
Project files for ImageD11 (fable ?)

- instrument description / parameters
   axes, rotations or translations
   beam energy
   etc   

- scan description
   image files
   detector used
   motors moved

- peaks
   x/y/omega etc

- grain parameters
   ubi / translation

- assignment of grains to peaks

"""

import yaml

class project( object ):
    def __init__(self, filename ):
        self.stuff = yaml.load( open(filename,"r") )
    def save( self, filename ):
        open(filename,"w").write( yaml.dump( self.stuff ) )
    def __repr__(self):
        return self.stuff 
    def __str__(self):
        return yaml.dump( self.stuff )


if __name__ == "__main__":
    import sys
    p = project( sys.argv[1] )
    print(p)
