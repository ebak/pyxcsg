# Copyright (c) 2021 Endre Bak
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


import os
import math
import shutil
from glm import vec2, vec3

from xcsg import save, LinearExtrude, tr, Circle, Square, Polygon, Rectangle, Sect2D, Fill2D, Hull2D, scale, Offset2D, \
    Minkowski2D, Projection2D, Cylinder, rotate, Z_AXIS, Cone, Cube, Box, Polyhedron, Sphere, mirror, Sect3D, move_to, \
    Minkowski3D, RotateExtrude, TransformExtrude, Sweep, Hull3D
from xcsg.common import Y_AXIS


def render(fpath, obj):
    dpath, name = os.path.split(fpath)
    dpath = os.path.join('samples', dpath)
    os.makedirs(dpath, exist_ok=True)
    xcsg_path = os.path.join(dpath, f'{name}.xcsg')
    obj_path = os.path.join(dpath, f'{name}.obj')
    save(xcsg_path, obj)
    if os.path.exists(obj_path):
        os.remove(obj_path)
    os.system(f'xcsg --obj {xcsg_path}')


def obj2d():
    def rdr(name, obj):
        render(f'2D_Objs/{name}', obj)
    #
    circle = LinearExtrude(dz=1)(
        tr([20, 0], Circle(r=10)))
    rdr('circle', circle)
    #
    square = LinearExtrude(dz=1)(Square(size=20, center=True))
    rdr('square', square)
    #
    polygon = LinearExtrude(dz=1)(
        Polygon(vertices=[
            vec2(0, 0), vec2(20, 0), vec2(20, 20), vec2(10, 30), vec2(0, 20)]))
    rdr('polygon', polygon)
    #
    rectangle = LinearExtrude(dz=1)(Rectangle(dx=20, dy=10))
    rdr('rectangle', rectangle)


def op2d():
    def rdr(name, obj):
        render(f'2D_Ops/{name}', obj)
    stuff = (
            Circle(r=3) + tr([20, 0], Square(size=6, center=True)) +
            tr([0, 20], Rectangle(dx=2, dy=5, center=True)))
    stuff += tr([0, -20], Circle(r=2.5))
    union2d = stuff
    union = LinearExtrude(dz=1)(stuff)
    rdr('union2d', union)
    #
    stuff = Square(size=30, center=True) - tr([-5, 8], Circle(r=2)) - tr([5, 8], Circle(r=2))
    stuff -= tr([0, 2], scale([1.5], Circle(r=2)))
    diff = LinearExtrude(dz=1)(stuff)
    rdr('diff2d', diff)
    poly_with_holes = stuff
    #
    sect = LinearExtrude(dz=1)(Sect2D()(tr([0, -8], Circle(r=15)), tr([0, 8], Circle(r=15))))
    rdr('intersection2d', sect)
    #
    stuff = LinearExtrude(dz=1)(Fill2D()(poly_with_holes))
    rdr('fill2d', stuff)
    #
    stuff = LinearExtrude(dz=1)(Hull2D()(union2d))
    rdr('hull2d', stuff)
    #
    stuff = LinearExtrude(dz=1)(Offset2D(delta=2, round=True)(Square(size=10)))
    rdr('offset2d', stuff)
    #
    stuff = LinearExtrude(dz=1)(Minkowski2D()(Rectangle(dx=200, dy=100, center=True), Circle(r=20)))
    rdr('minkowski2d', stuff)


def op2d_to_3d():
    def rdr(name, obj):
        render(f'2D_to_3D_Ops/{name}', obj)
    #
    rdr('linear_extrude', LinearExtrude(dz=10)(Square(size=40, center=True) - Circle(r=17)))
    #
    rdr('rotate_extrude', RotateExtrude(angle=1.0472, pitch=0)(tr([10], Square(size=10))))
    #
    rdr(
        'transform_extrude',
        TransformExtrude()(
            Offset2D(delta=10, round=True)(Square(size=60, center=True)),
            tr([0, 0, 50], Circle(r=30))))
    #
    v = vec3(0, 1, 0)
    rdr(
        'sweep',
        Sweep(
            spline_path=(
                (vec3(0, 0, 0), v),
                (vec3(0, -1.17, 10), v),
                (vec3(0, -4.13, 20), v),
                (vec3(0, -7.50, 30), v),
                (vec3(0, -9.70, 40), v),
                (vec3(0, -9.70, 50), v),
                (vec3(0, -7.50, 60), v),
                (vec3(0, -4.13, 70), v),
                (vec3(0, -1.17, 80), v),
                (vec3(0,  0.00, 90), v))
        )(
            Rectangle(dx=8, dy=1, center=True) + Rectangle(dx=1, dy=6)))


def op3d_to_2d():
    def rdr(name, obj):
        render(f'3D_to_2D_Ops/{name}', obj)
    stuff = LinearExtrude(dz=1)(
        Projection2D()(
            rotate(
                ang=math.radians(30), axis=Z_AXIS,
                obj=scale((2, 1), Cylinder(h=100, r=30)))))
    rdr('projection2d', stuff)


def obj3d():
    def rdr(name, obj):
        render(f'3D_Objs/{name}', obj)
    #
    rdr('cone', Cone(h=40, r1=20, r2=8))
    #
    rdr('cube', Cube(size=30))
    #
    rdr('cuboid', Box(dx=10, dy=20, dz=30))
    #
    rdr('cylinder', Cylinder(h=40, r=15))
    #
    rdr(
        'polyhedron',
        Polyhedron(
            vertices=[
                vec3(-10, -10, -10), vec3(10, -10, -10), vec3(10, 10, -10), vec3(-10, 10, -10),
                vec3(0, 0, 10)],
            faces=[(3, 2, 1, 0), (0, 1, 4), (1, 2, 4), (2, 3, 4), (3, 0, 4)]))
    #
    rdr('sphere', Sphere(r=50))


def op3d():
    def rdr(name, obj):
        render(f'3D_Ops/{name}', obj)
    rdr('union3d', Cube(size=50) + Sphere(r=33))
    #
    rdr('diff3d', Cube(size=50, center=True) - Sphere(r=33))
    #
    rdr('intersection3d', Sect3D()(Cube(size=50, center=True), Sphere(r=33)))
    #
    rdr('hull3d', Hull3D()(Cube(size=50, center=True), move_to([25, 25], Sphere(r=33))))
    #
    rdr('minkowski3d',
        Minkowski3D()(
            Cube(size=100) + Box(dx=40, dy=40, dz=150),
            Sphere(r=20)))


def transforms():
    def rdr(name, obj):
        render(f'Transforms/{name}', obj)

    stuff = Cylinder(r=3, h=10) + tr([0, 0, 16], Sphere(r=3))
    stuff += mirror(normal=[1, 0, 1], obj=stuff)
    rdr('mirror', stuff)
    #
    rdr('rotate', rotate(ang=math.radians(30), axis=Y_AXIS, obj=Cylinder(r=1, h=20)))
    #
    rdr('scale', scale([3, 1], Sphere(r=10)))


if __name__ == '__main__':
    if os.path.exists('samples'):
        shutil.rmtree('samples', ignore_errors=True)
    os.mkdir('samples')
    obj2d()
    op2d()
    op2d_to_3d()
    op3d_to_2d()
    obj3d()
    op3d()
    transforms()

