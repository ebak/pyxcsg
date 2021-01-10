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

import glm

from lxml import etree
from xcsg.impl import Obj2D, mk_node, FlattenerOp2D, MoreChildren, OneChild, Obj3D, TwoChildren, FlattenerOp3D


# -------------------------------------------------------
#                    2D objects
# -------------------------------------------------------
class Circle(Obj2D):

    def __init__(self, r):
        super().__init__('circle', r=r)


class Square(Obj2D):

    def __init__(self, size, center=False):
        super().__init__('square', size=size, center=center)


class Polygon(Obj2D):

    def __init__(self, vertices):
        super().__init__('polygon')
        self.vertices = vertices

    def _get_child_nodes(self):
        verts = mk_node('vertices')
        for v in self.vertices:
            verts.append(mk_node('vertex', x=v.x, y=v.y))
        return [verts]


class Rectangle(Obj2D):

    def __init__(self, dx, dy, center=False):
        super().__init__('rectangle', dx=dx, dy=dy, center=center)


# -------------------------------------------------------
#                    2D operations
# -------------------------------------------------------
class Union2D(FlattenerOp2D):
    def __init__(self):
        super().__init__('union2d')


class Diff2D(FlattenerOp2D):
    def __init__(self):
        super().__init__('difference2d')


Difference2D = Diff2D


class Intersection2D(Obj2D):

    def __init__(self):
        super().__init__('intersection2d', MoreChildren(Obj2D))


Sect2D = Intersection2D


class Fill2D(Obj2D):

    def __init__(self):
        super().__init__('fill2d', OneChild(Obj2D))


class Hull2D(Obj2D):

    def __init__(self):
        super().__init__('hull2d', MoreChildren(Obj2D))


class Offset2D(Obj2D):

    def __init__(self, delta, round, chamfer=False):
        super().__init__('offset2d', OneChild(Obj2D), delta=delta, round=round, chamfer=chamfer)


class Minkowski2D(Obj2D):

    def __init__(self):
        super().__init__('minkowski2d', TwoChildren(Obj2D))


# -------------------------------------------------------
#                3D to 2D operations
# -------------------------------------------------------
class Projection2D(Obj2D):

    def __init__(self):
        super().__init__('projection2d', OneChild(Obj3D))


# -------------------------------------------------------
#                    3D objects
# -------------------------------------------------------
class Cone(Obj3D):

    def __init__(self, r1, r2, h, center=False):
        super().__init__('cone', r1=r1, r2=r2, h=h, center=center)


class Cube(Obj3D):

    def __init__(self, size, center=False):
        super().__init__('cube', size=size, center=center)


class Cuboid(Obj3D):

    def __init__(self, dx, dy, dz, center=False):
        super().__init__('cuboid', dx=dx, dy=dy, dz=dz, center=center)


Box = Cuboid    # :)


class Cylinder(Obj3D):

    def __init__(self, r, h, center=False):
        super().__init__('cylinder', r=r, h=h, center=center)


class Polyhedron(Obj3D):

    def __init__(self, vertices, faces):
        """
        vertices: [glm.vec3, ...]
        faces: [(vertex_index, ...), ...]
        """
        super().__init__('polyhedron')
        self.vertices, self.faces = vertices, faces

    def _get_child_nodes(self):
        verts = mk_node('vertices')
        for v in self.vertices:
            verts.append(mk_node('vertex', x=v.x, y=v.y, z=v.z))
        faces = mk_node('faces')
        for f in self.faces:
            face = mk_node('face')
            faces.append(face)
            for idx in f:
                face.append(mk_node('fv', index=idx))
        return [verts, faces]


class Sphere(Obj3D):

    def __init__(self, r):
        super().__init__('sphere', r=r)


# -------------------------------------------------------
#                2D to 3D operations
# -------------------------------------------------------
class LinearExtrude(Obj3D):

    def __init__(self, dz):
        super().__init__('linear_extrude', OneChild(Obj2D), dz=dz)


class RotateExtrude(Obj3D):

    def __init__(self, angle, pitch):
        super().__init__('rotate_extrude', OneChild(Obj2D), angle=angle, pitch=pitch)


class TransformExtrude(Obj3D):

    def __init__(self):
        super().__init__('transform_extrude', TwoChildren(Obj2D))


class Sweep(Obj3D):

    def __init__(self, spline_path):
        """spline_path: [(p: vec3, v: vec3)]"""
        super().__init__('sweep', OneChild(Obj2D))
        self.spline_path = spline_path

    def _get_child_nodes(self):
        e = mk_node('sweep')
        e.append(self.objs[0].to_element())
        sp = mk_node('spline_path')
        e.append(sp)
        for p, v in self.spline_path:
            sp.append(mk_node('cpoint', x=p.x, y=p.y, z=p.z, vx=v.x, vy=v.y, vz=v.z))
        return e


# -------------------------------------------------------
#                    3D operations
# -------------------------------------------------------
class Union3D(FlattenerOp3D):
    def __init__(self):
        super().__init__('union3d')


class Diff3D(FlattenerOp3D):
    def __init__(self):
        super().__init__('difference3d')


Difference3D = Diff3D


class Intersection3D(Obj3D):
    def __init__(self):
        super().__init__('intersection3d', MoreChildren(Obj3D))


Sect3D = Intersection3D


class Hull3D(Obj3D):
    def __init__(self):
        super().__init__('hull3d', MoreChildren(Obj3D))


class Minkowski3D(Obj3D):
    def __init__(self):
        super().__init__('minkowski3d', MoreChildren(Obj3D))


def to_vec3(v):
    if isinstance(v, (list, tuple)):
        if len(v) < 3:
            v = list(v) + [0 for _ in range(3 - len(v))]
            return glm.vec3(v)
        return glm.vec3(v)
    elif not isinstance(v, glm.vec3):
        return glm.vec3(v)
    return v


def to_vec4(v):
    if isinstance(v, glm.vec4):
        return v
    if isinstance(v, (list, tuple)):
        if len(v) < 4:
            return glm.vec4(to_vec3(v), 0)
        return glm.vec4(v)
    assert False


def translate(v, obj):
    obj = obj.copy()
    v = to_vec4(v)
    if False:   # works only with newer PyGLM
        print(f'v: {v}')
        print(f'mm:\n{obj.model_matrix}')
        obj.model_matrix[3] += v
        print(f'modified mm:\n{obj.model_matrix}')
    else:
        l = glm.vec4(obj.model_matrix[3]) + v
        # print(f'{obj.__class__.__name__} l: {l}')
        obj.model_matrix[3] = l
        # print(f'modified mm:\n{obj.model_matrix}')
    return obj


tr = move_to = translate


def rotate(ang, axis, obj):
    obj = obj.copy()
    rm = glm.mat4x4()
    rm = glm.rotate(rm, ang, axis)
    obj.model_matrix = rm * obj.model_matrix
    return obj


def scale(v, obj):
    obj = obj.copy()
    # set missing dimensions to 1
    if isinstance(v, (list, tuple)) and len(v) < 3:
        v = list(v) + [1 for _ in range(3 - len(v))]
    obj.model_matrix = glm.scale(obj.model_matrix, to_vec3(v))
    return obj


def mirror_vector(axis_unit, v):
    prj_len = glm.dot(axis_unit, v)
    scaled_axis = 2 * prj_len * axis_unit
    return v - scaled_axis


def mirror(axis, obj):
    obj = obj.copy()
    axis_unit = glm.normalize(to_vec3(axis))
    mm = obj.model_matrix
    i, j, k, l = [mirror_vector(axis_unit, mm[i].xyz) for i in range(4)]
    mm[0], mm[1], mm[2] = [glm.vec4(v, 0) for v in (i, j, k)]
    mm[3] = glm.vec4(l, 1)
    return obj


def to_xml(obj, secant_tolerance=0.01):
    assert isinstance(obj, Obj3D)
    root = mk_node('xcsg', version='1.0', secant_tolerance=secant_tolerance)
    root.append(obj.to_element())
    return root


def save(file_path, obj, secant_tolerance=0.01):
    root = to_xml(obj, secant_tolerance=secant_tolerance)
    with open(file_path, 'w') as f:
        f.write(etree.tostring(root, encoding='utf-8', pretty_print=True).decode())
