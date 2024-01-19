'''
Module resposible for holding Curve class that holds information
about the slider curve, as well as having functions to calculate the curve.
'''

import pygame

# credits for bezier curve functions:
# https://codereview.stackexchange.com/questions/240710/pure-python-bézier-curve-implementation

def bezier_curve(control_points, number_of_curve_points) -> list:
    '''
    Generates a bezier curve from control points and returns a list
    of points on a curve
    '''
    return [
        bezier_point(control_points, t)
        for t in (
            i / (number_of_curve_points - 1) \
                for i in range(number_of_curve_points)
        )
    ]

def bezier_point(control_points, t):
    '''
    Helper function for generating bezier curve
    '''
    if len(control_points) == 1:
        result, = control_points
        return result
    control_linestring = zip(control_points[:-1], control_points[1:])
    return bezier_point(
        [(1 - t) * p1 + t * p2 for p1, p2 in control_linestring], t)

class Curve:
    def __init__(self, 
                 control_points: list,
                 divisions: int = 120) -> None:
        self.CTPoints = control_points
        self.divisions = divisions
        self.points = []
        
  
    def get_bezier_path(self, scale_factor, pos_x, pos_y) -> list:
        '''
        Returns a path of the curve scaled and placed in the playfield.
        '''
        for point in self.CTPoints:
            x = point[0] * scale_factor
            y = point[1] * scale_factor
            x += pos_x
            y += pos_y
            x = int(x)
            y = int(y)
            self.points.append(complex(x,y))
        return self.get_points()

    def get_points(self) -> list:
        '''
        Generates points on a curve by calling curve generation functions.
        '''
        res = bezier_curve(self.points, self.divisions)
        return [(int(x.real), int(x.imag)) for x in res]
