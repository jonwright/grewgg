

from __future__ import print_function, division

import sys, os, unittest
import numpy as np

from ImageD11 import parameters, columnfile, transform
from grewgg import general_geometry

TEST="./testdata"

parfiles = ["test%d.par"%(i) for i in range(5)] 

class test_xyz_match( unittest.TestCase ):
    
    def test_xyz(self):
        for p in parfiles:
            parfile = os.path.join( TEST,  p )
            fltfile = os.path.join( TEST,  "test.flt" )
            pars = parameters.read_par_file( parfile ).parameters
            colf = columnfile.columnfile( fltfile )
            sc = colf.sc
            fc = colf.fc
            geometry = general_geometry.fable_detector( pars,
                                                        noisy=False)
            # test old
            xyz1 = transform.compute_xyz_lab( (sc, fc),
                                          **pars )
            # test new
            v = np.zeros( (3, len( sc ) ) )
            v[1] = fc
            v[2] = sc
            xyz2 = geometry( (np.zeros(len(fc)), fc, sc) )
            if not np.allclose( xyz1, xyz2 ):
                print("Geometry",geometry)
                print("Parfile:",p)
                for i in range(len(fc)):
                    print(xyz1[:,i])
                    print(xyz2[:,i])
                    print()
            assert np.allclose( xyz1, xyz2 )  


    def test_xyz_from_yaml(self):
        for p in parfiles:
            parfile = os.path.join( TEST,  p )
            fltfile = os.path.join( TEST,  "test.flt" )
            ymlfile = os.path.join(
                os.path.split(general_geometry.__file__)[0],
                "data",
                "fable.yml" )
            pars = parameters.read_par_file( parfile ).parameters
            colf = columnfile.columnfile( fltfile )
            sc = colf.sc[:4]
            fc = colf.fc[:4]
            geometry = general_geometry.from_yml( pars,
                                                  ymlfile,
                                                  path=[ "Positioners", "Fable_detector"],
                                                  noisy=False )
            # test old
            xyz1 = transform.compute_xyz_lab( (sc, fc),
                                          **pars )
            # test new
            v = np.zeros( (3, len( sc ) ) )
            v[1] = fc
            v[2] = sc
            xyz2 = geometry( (np.zeros(len(fc)), fc, sc) )
            if not np.allclose( xyz1, xyz2 ):
                print("Geometry",geometry)
                print("Parfile:",p)
                for i in range(len(fc)):
                    print(xyz1[:,i])
                    print(xyz2[:,i])
                    print()
            assert np.allclose( xyz1, xyz2 )  

        
        
if __name__ ==  "__main__":
    unittest.main()
