
from __future__ import print_function, division
import sys
import yaml
import numpy as np
from . import positioners

def fable_detector( pars , noisy=False ):
    """
    Takes a fable parameter dictionary and computes a static positioner
    """
    # mapping sc, fc to 3-vector as [0, fc, sc]
    # was:             
    # [ o11, o12 ] . [(pks[0]-zc)*zs  == sc]
    # [ o21, o22 ]   [(pks[1]-yc)*ys  == fc]
    #
    # now / future
    #  x=0
    #  y=fc
    #  z=sc
    #
    # FIXME : convert this list to YML !!

    
    y_size = pars["y_size"]
    z_size = pars["z_size"]
    fable_detector_geometry = [ # one is first applied first to vector
        positioners.translation( "y_center", [0,-1,0], pars["y_center"] ),
        positioners.translation( "z_center", [0,0,-1], pars["z_center"] ),
        positioners.scale( "y_size", [0, 1, 0], pars["y_size"] ),
        positioners.scale( "z_size", [0, 0, 1], pars["z_size"]  ),
        positioners.positioner( "Oij",
                                np.array(
                                    [[1,          0,           0, 0],
                                     [0,pars["o22"], pars["o21"], 0],
                                     [0,pars["o12"], pars["o11"], 0],
                                     [0,          0,           0, 1]] ) ),
        positioners.rotation( "tilt_z", [0,0,1], np.degrees( pars["tilt_z"] )),
        positioners.rotation( "tilt_y", [0,1,0], np.degrees( pars["tilt_y"] )),
        positioners.rotation( "tilt_x", [1,0,0], np.degrees( pars["tilt_x"] )),
        positioners.translation( "distance", [1,0,0], pars["distance"] ),
        ]
    p = positioners.positioner( "fable_detector:" )
    pl = []
    for item in fable_detector_geometry:
        if noisy:
            print(p)
            print(item)
        p = item*p
        if noisy:
            print(p)
            print("---")
    return p





def fable_sample( pars, noisy=False ):
    """
    Takes a fable parameter dictionary and returns a 
    diffractometer which moves vectors with omega
    """
    d = yaml.load( open("fable.yml","r") )
#    print(d)
    description = d['Positioners']['Fable_diffractometer']
    p = positioners.positioner( "Fable_diffractometer" )
    pl = []
    #  reverse order
    for itemdesc in description[::-1]:
        item = positioners.create( itemdesc, pars )
        pl.append(item)
        p = item*p
        if noisy:
            print(item)
    return p

def from_yml( pars, ymlfile, path,  noisy=False ):
    """
    Takes a fable parameter dictionary and returns a 
    diffractometer which moves vectors with omega
    """
    description = yaml.load( open(ymlfile,"r") )
    for name in path:
        description = description[name]
    p = positioners.positioner(".".join(path) ) # identity
    pl = []
    #  note the reverse order
    for itemdesc in description[::-1]:
        item = positioners.create( itemdesc, pars )
        pl.append(item)
        p = item*p
        if noisy:
            print(item)
    return p


        
if __name__=="__main__":
    import sys
    from ImageD11 import parameters
    pars = parameters.read_par_file( sys.argv[1] ).parameters
    print( fable_detector( pars ) )
    print( fable_sample( pars ) )
    from_yml( pars, "fable.yml", ["Positioners", "Fable_diffractometer"] )
    from_yml( pars, "fable.yml", ["Positioners", "Fable_detector"] )
