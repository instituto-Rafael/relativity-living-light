import math
import unittest
from rx.spatial_diagonal_geometry import (
    sky_direction, tangent_frame_components, spatial_diagonal,
    nonplanarity_four_points, hex_oblique_diagonal, tilted_ellipse_point)

class SpatialDiagonalTests(unittest.TestCase):
    def test_direction_unknown_depth(self):
        r=sky_direction(0.,0.)
        self.assertEqual(r['direction'], (1.,0.,0.))
        self.assertIsNone(r['position'])
        self.assertEqual(r['distance_status'],'TOKEN_VAZIO_LINE_OF_SIGHT_DISTANCE')
        self.assertFalse(r['claim_allowed'])

    def test_distance_explicit(self):
        r=sky_direction(0.,0.,2.)
        self.assertEqual(r['position'],(2.,0.,0.))
        self.assertEqual(r['distance_status'],'DISTANCE_SUPPLIED_NOT_INFERRED')

    def test_poles_and_invalid(self):
        self.assertAlmostEqual(sky_direction(0,math.pi/2)['direction'][2],1.)
        for args in ((0,2), (math.nan,0), (0,0,0), (0,0,-1)):
            with self.assertRaises(ValueError):sky_direction(*args)

    def test_diagonals_2d_3d(self):
        d=spatial_diagonal((0,0,0),(1,1,1),0,0)
        self.assertAlmostEqual(d['diagonal_3d'],math.sqrt(3))
        self.assertAlmostEqual(d['diagonal_2d'],math.sqrt(2))
        self.assertAlmostEqual(d['line_of_sight'],1.)
        self.assertAlmostEqual(d['diagonal_2d']**2+d['line_of_sight']**2,3.)
        self.assertFalse(d['claim_allowed'])

    def test_roundtrip_and_scale(self):
        for theta in (0,math.pi/6,math.pi/2,-math.pi/3):
            for ra,dec in ((0,0),(math.pi/2,0),(.6,.4)):
                v=(2.0*math.cos(theta),2.0*math.sin(theta),1.3)
                c=tangent_frame_components(v,ra,dec)
                self.assertAlmostEqual(c['diagonal_3d']**2,
                    c['east']**2+c['north']**2+c['line_of_sight']**2,places=12)
        c1=tangent_frame_components((1,2,3),.1,.3)
        c2=tangent_frame_components((1e8,2e8,3e8),.1,.3)
        self.assertAlmostEqual(c2['diagonal_3d']/1e8,c1['diagonal_3d'])

    def test_oblique_hexagon(self):
        self.assertAlmostEqual(hex_oblique_diagonal(1,1),math.sqrt(3))
        self.assertAlmostEqual(hex_oblique_diagonal(1,-1),1.)
        with self.assertRaises(ValueError): hex_oblique_diagonal(float('nan'),0)

    def test_four_point_nonplanarity(self):
        x=nonplanarity_four_points(((0,0,0),(1,0,0),(0,1,0),(0,0,1)))
        self.assertEqual(x['state'],'DEFINED_GEOMETRY_ONLY')
        self.assertAlmostEqual(x['index'],1.)
        y=nonplanarity_four_points(((0,0,0),(1,0,0),(0,1,0),(0,0,-1)))
        self.assertAlmostEqual(y['index'],-1.)
        z=nonplanarity_four_points(((0,0,0),(1,0,0),(0,1,0),(1,1,0)))
        self.assertEqual(z['index'],0.)
        for bad in (((0,0,0),(1,0,0),(0,1,0)), ((0,0,0),)*5):
            with self.assertRaises(ValueError):nonplanarity_four_points(bad)
        deg=nonplanarity_four_points(((0,0,0),(0,0,0),(0,1,0),(0,0,1)))
        self.assertEqual(deg['state'],'TOKEN_VAZIO_DEGENERATE_CHORD')

    def test_ellipse_3d(self):
        out=tilted_ellipse_point((0,0,0),(1,0,0),(0,0,1),3,2,0)
        self.assertEqual(out['position'],(3.,0.,0.))
        self.assertEqual(out['tangent'],(0.,0.,2.))
        self.assertEqual(out['plane_normal'],(0.,-1.,0.))
        self.assertFalse(out['claim_allowed'])
        for v in ((1,0,0),(.1,1,0)):
            with self.assertRaises(ValueError):
                tilted_ellipse_point((0,0,0),(1,0,0),v,3,2,0)

    def test_reject_invalid_vectors(self):
        for vector in ((1,float('nan'),0), (0,0), None):
            with self.assertRaises(ValueError):tangent_frame_components(vector,0,0)
        with self.assertRaises(ValueError):spatial_diagonal((0,0,0),(math.inf,0,0),0,0)

if __name__=='__main__':unittest.main()
