
import unittest
import numpy as np

from grewgg import positioners


class test_translation( unittest.TestCase ):
    
    def setUp(self):
        self.tx = positioners.translation( "samtx", [1,0,0], 0.0 )
        self.ty = positioners.translation( "samty", [0,1,0], 0.0 )
        self.tz = positioners.translation( "samtz", [0,0,1], 0.0 )
        
    def test_1_1(self):
        v = [0,0,0]
        assert np.allclose( self.tx(v, 0  ), v )
        assert np.allclose( self.tx(v, 1  ), [1,0,0] )
        assert np.allclose( self.tx(v, 3.3), [3.3,0,0] )
        assert np.allclose( self.ty(v, 0  ), v )
        assert np.allclose( self.ty(v, 1  ), [0,1,0] )
        assert np.allclose( self.ty(v, 3.3), [0,3.3,0] )
        assert np.allclose( self.tz(v, 0  ), v )
        assert np.allclose( self.tz(v, 1  ), [0,0,1] )
        assert np.allclose( self.tz(v, 3.3), [0,0,3.3] )

    def test_4_1(self):
        v = np.array( [ [0,0,0], [0,0,0], [0,0,0], [0,0,0] ] )
        vt = np.array( [ t + (1,0,0) for t in v ] ).T
        assert np.allclose( self.tx(v.T, 1), vt )

    def test_4_4(self):
        v = np.array( [ [0,0,0], [0,2,0], [0,1,0], [0,0,1] ] )
        p = np.array( [ 1, 2, 3, 4] )
        vt = np.array([ tt + (pp,0,0) for tt,pp in zip(v, p) ]).T
        assert vt.shape == (3,4)
        assert np.allclose( self.tx(v.T, p), vt )

    def test_inv(self):
        itx = self.tx.inv()
        v = np.array( [ [0,0,0], [0,2,0], [0,1,0], [0,0,1] ] )
        p = np.array( [ 1, 2, 3, 4] )
        vt = np.array([ tt + (pp,0,0) for tt,pp in zip(v, p) ]).T
        assert np.allclose( itx ( vt, -p ), self.tx( vt, p ) )

        
class test_rotation( unittest.TestCase ):
    
    def setUp(self):
        self.rx = positioners.rotation('rx', [1.0, 0.0, 0.0], 0.0 )
        self.ry = positioners.rotation('ry', [0.0, 0.1, 0.0], 0.0 )
        self.rz = positioners.rotation('rz', [0.0, 0.0, 2.0], 0.0 )
        self.rz45 = positioners.rotation('rz', [0.0, 0.0, 2.0], 45.0 )

    def test_rh(self):
        # rotation about x +90   y +90  z +90
        #         ^z    x -> x   z->x   x->y
        #         |     y -> z   y->y   y->-x
        #  x <----|     z -> -y  x->-z  z->z
        #       y/
        v = np.array( [ [ 1,0,0], [0,1,0], [0,0,1], [0,0,0] ] ).T
        vx90 = np.array([ [1,0,0], [0,0,1], [0,-1,0], [0,0,0] ]).T
        vy90 = np.array([ [0,0,-1], [0,1,0], [1,0,0], [0,0,0] ]).T
        vz90 = np.array([ [0,1,0], [-1,0,0], [0,0,1], [0,0,0] ]).T
        assert v.shape == vx90.shape == vy90.shape == vz90.shape == (3,4)
        for vtest, vx, vy, vz in zip( v.T, vx90.T, vy90.T, vz90.T ):
            assert np.allclose( self.rx( vtest, 90.0 ), vx ), (
                vtest,vx,self.rx(vtest,90.0))
            assert np.allclose( self.ry( vtest, 90.0 ), vy )
            assert np.allclose( self.rz( vtest, 90.0 ), vz )
        assert np.allclose( self.rx( v, 90.0 ), vx90 )
        assert np.allclose( self.ry( v, 90.0 ), vy90 )
        assert np.allclose( self.rz( v, 90.0 ), vz90 )
        # Check an inverse
        irz = self.rz.inv()
        assert np.allclose( irz( v, -90.0 ), vz90 )

    def test_mul(self):
        v = np.array( [ [ 1,0,0], [0,1,0], [0,0,1], [0,0,0] ] ).T
        v1 = self.rz45( v )
        v2 = self.rz45 * v
        assert np.allclose( v1, v2 )


class test_rot_trans( unittest.TestCase ):
    
    def setUp(self):
        self.rz = positioners.rotation('rz', [0.0, 0.0, 2.0], 90.0 )
        self.ry = positioners.rotation('ry', [0.0, 2.0, 0.0], 45.0 )
        self.ty = positioners.translation("ty" , [0.,1.,0.], 12. )
        self.c = self.ry * self.ty * self.rz

    def test_print(self):
        s = str(self.ry)+str(self.ty)+str(self.c)
        assert type(s) == type("string")
        
    def test_rt(self):
        """check a combined roation and translation """
        v = np.array([ [ 1,0,0], [0,1,0], [0,0,1], [0,0,0] ]).T
        rz_v = self.rz( v )
        ty_rz_v_1 = self.ty( rz_v )
        ty_rz = self.ty * self.rz
        ty_rz_v_2 = ty_rz( v )
        assert np.allclose( ty_rz_v_1, ty_rz_v_2)

    def test_rt_2(self):
        """ check the product of 3 """
        v = np.array([ [ 1,0,0], [0,1,0], [0,0,1], [0,0,0] ]).T
        v1 = self.ry( self.ty( self.rz( v ) ) )
        v2 = self.c(v)
        assert np.allclose( v1, v2), (v1.T,v2.T)

    def test_inv(self):
        """ check the inverse"""
        v = np.array([ [ 1,0,0], [0,1,0], [0,0,1], [0,0,0] ]).T
        vtrans = self.c(v)
        ci = self.c.inv()
        vorig = ci * vtrans
        # check they come back
        assert np.allclose( v, vorig )
        assert not np.allclose( v, vtrans ) 
        

        
        
if __name__ ==  "__main__":
    unittest.main()
