
# for python2/python3
from __future__ import print_function

import numpy as np


class positioner( object ):
    """ Base class for positioners
    Uses a 4x4 transformation matrix which is: [ [ U  t ][ 0  1 ] ]
    Only one position allowed (cannot change angles/distance)
    using this class.
    Call operation used to apply transformation to (3,N) vectors
    Multiply operation used for chaining operations (or calls)
    """
    def __init__(self, name, m4=np.eye(4)):
        """ Store a name for the axis and the matrix"""
        self.name = name
        self.m4 = m4
        assert m4.shape == (4,4)
    def mat4(self):
        """ Function getter - other positioners to override """
        return self.m4
    def __call__(self, v):
        """ If v is a vec[3][N] we compute m4.v """
        va = np.asarray( v ) 
        rot = np.dot( self.m4[:3,:3], va )
        t   = self.m4[:3,3]
        return rot + t[:,np.newaxis]
    def __mul__(self, other):
        """ Chain together two positioner operations via their mat4 """
        if isinstance( other, positioner ):
            m4 = np.dot( self.mat4(), other.mat4() )
            return positioner( "%s.%s"%(self.name,other.name), m4 )
        else:
            return self( other )
    def __str__( self ):
        """For printing"""
        return str(type(self))+self.name+"\n"+str( self.mat4() )
    def inv( self ):
        """ inverse """
        return positioner( self.name+"'", np.linalg.inv( self.mat4() ) )


class translation( positioner ):
    """ Translations
    position is the axis position
    axis takes into account the units (not normalised)
    """
    def __init__(self, name, axis, position):
        """ Axis is a direction, not normalised """
        self.name = name
        self.axis = np.asarray( axis )
        self.position = position
        
    def mat4(self):
        m4 = np.eye(4)
        m4[:3,3] = self.axis * self.position
        return m4
    
    def __call__(self, v, position = None):
        """
        v is (3, N) vector
        position is a scalar or N vector
        """
        if position is None:
            pa = np.asarray( self.position )
        else:
            pa = np.asarray( position )
        if len(pa.shape) == 0:
            va = np.asarray(v)
            return (va.T + self.axis * pa).T
        assert len(v) == len(self.axis)
        assert len(pa) == len(v[0])
        return v + pa * self.axis[:,np.newaxis]

    def __str__(self):
        return"%s:%s\n\taxis: %s\n\tposition: %s"%(
            str(type(self)),
            self.name,
            str( self.axis ),
            str( self.position ) )

    def inv( self ):
        """ inverse  - reverses positions
        ... must invert the axis to allow pos to vary later
        """
        return translation( self.name+"'", -self.axis, self.position )

    
class scale( positioner ):
    """ Change of units probably - rescale things
    """
    def __init__(self, name, axis, position):
        """ Axis is a direction, not normalised """
        self.name = name
        v = np.asarray( axis ).astype( int )
        assert v.sum()==1 and (v>0).sum() == 1, "scale type is for x or y or z"
        self.position = position
        self.scalevec = float(position)*v + (1-v)        
        
    def mat4(self):
        m4 = np.eye(4)
        m4[0,0] = self.scalevec[0]
        m4[1,1] = self.scalevec[1]
        m4[2,2] = self.scalevec[2]
        return m4
    
    def __call__(self, v, position = None):
        """
        v is (3, N) vector
        position is a scalar or N vector
        """
        assert position is None
        return v * self.scalevec

    def __str__(self):
        return"%s:%s\n\tscales: %s"%(
            str(type(self)),
            self.name,
            str( self.scalevec ))

    def inv( self ):
        """ inverse  - reverses positions
        ... must invert the scale... 
        """
        return scale( self.name+"'", self.axis, 1.0/self.position )


class rotation( positioner ):
    """ Rotation axes using axis/angle description """
    def __init__(self, name, axis, position):
        """ name of the motor
        axis direction for right handed rotation
        position is current position
        """
        self.name = name
        self.axis = np.asarray( axis )
        self.position = position
        # Check the axis is a unit vector
        n = np.linalg.norm( self.axis )
        assert n>0
        self.axis = self.axis / n
        self.matrix = self.make_matrix( self.position )

    def inv( self ):
        """ inverse  - reverses action
        ... must invert the axis to allow pos to vary later
        """
        return rotation( self.name+"'", -self.axis, self.position )


    def mat4(self):
        m4 = np.eye(4)
        m4[:3,:3] = self.make_matrix( self.position )
        return m4
    
    def axis_angle( self, v, position = None):
        """ Use when position may be different for each x 
        a = axis
        vrot = cos(p).v + sin(p).(axv) + (1-cos(p))(a.v).a
        """
        if position is None:
            p = np.radians( self.position )
        else:
            p = np.radians( position )
        va   = np.asarray( v )
        cosp = np.cos(p)
        sinp = np.sin(p)
        vrot = cosp * va
        vrot += sinp * np.cross( va, self.axis )
        ava = np.dot( va, self.axis )[:, np.newaxis] * self.axis
        vrot += ava*(1-cosp)
        return vrot

    def make_matrix(self, angle_deg):
        """ Convert to rotation matrix representation 
        for a given angle in degrees
        TODO : cache/memoize values ? 
        """
        return self.axis_angle( [[ 1, 0, 0],
                                 [ 0, 1, 0],
                                 [ 0, 0, 1]], position=angle_deg )
    
    def matvec( self, v, position = None ):
        """ Uses rotation matrix to rotate a bunch of vectors
        The vectors are (3,N) memory layout
        Position must be the same for all N, so a scalar or None
        Does NOT update self.position (write that if you want to)
        """
        va = np.asarray( v )
        if position is None:
            return np.dot( self.matrix, va )
        else:
            assert len(np.asarray( position ).shape) == 0
            mat = self.make_matrix( position )
            return np.dot( mat, va )
        
    def __call__(self, v, position = None):
        """
        v is (N, 3) vector
        position is a (3,) vector
        """
        if position is None:
            return self.matvec( v, position )
        pa = np.asarray( position )
        if len(pa.shape) == 0: # scalar
            return self.matvec( v, position )
        else:
            return self.axis_angle( v, position )

    def __str__(self):
        return"%s:%s\n\taxis: %s\n\tposition: %s"%(
            str(type(self)),
            self.name,
            str( self.axis ),
            str( self.position ) )
        

def interpret( symbol, pars ):
    if symbol in pars:
        return float(pars[symbol])
    else:
        return float(symbol)

    
def create( ymld, pars ):
    
    name  = ymld['name']
    typ   = ymld['type']

    if typ in ['rotation','translation','scale']:
        pos   = 0
        axis  = ymld[ 'axis' ]
        if pos in ymld:
            pos = ymld['pos']
        if name in pars:
            pos = pars[name]
            
        if ymld['type'] == "translation":
            return translation( name, axis, pos )
        
        if ymld['type'] == "rotation":
            if name.find("tilt") == 0:
                pos = np.degrees( pos )
            return rotation( name, axis, pos )

        if ymld['type'] == "scale":
            return scale( name, axis, pos )
        
    if typ == "positioner":
        m4 = [[ interpret( symbol, pars ) for symbol in row]
              for row in ymld['mat4']]
        return positioner( name, np.array(m4) )
                
    raise Exception("Cannot figure out"+str(ymld))
    
    

class instrument( object ):
    """ Represents an instrument as a stack of positioners """
    def __init__(self, name, positioners):
        pass
