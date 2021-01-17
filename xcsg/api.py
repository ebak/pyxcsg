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
from typing import List, Tuple, Union

import glm

from lxml import etree
from xcsg.impl import Obj2D, mk_node, FlattenerOp2D, MoreChildren, OneChild, Obj3D, TwoChildren, FlattenerOp3D, \
    pre_process, Obj


# -------------------------------------------------------
#                    2D objects
# -------------------------------------------------------
class Circle(Obj2D):

    def __init__(self, r: float):
        """
        `See. <https://github.com/arnholm/xcsg/wiki/circle>`__

        :param r: radius
        """
        super().__init__('circle', r=r)


class Square(Obj2D):

    def __init__(self, size: float, center: bool = False):
        """
        `See. <https://github.com/arnholm/xcsg/wiki/square>`__

        :param size:
        :param center:
        """
        super().__init__('square', size=size, center=center)


class Polygon(Obj2D):

    def __init__(self, vertices: List[glm.vec2]):
        """
        `See. <https://github.com/arnholm/xcsg/wiki/polygon>`__

        :param vertices:
        """
        super().__init__('polygon')
        self.vertices = vertices

    def _get_child_nodes(self):
        verts = mk_node('vertices')
        for v in self.vertices:
            verts.append(mk_node('vertex', x=v.x, y=v.y))
        return [verts]


class Rectangle(Obj2D):

    def __init__(self, dx: float, dy: float, center: bool = False):
        """
        `See. <https://github.com/arnholm/xcsg/wiki/rectangle>`__

        :param dx:
        :param dy:
        :param center:
        """
        super().__init__('rectangle', dx=dx, dy=dy, center=center)


# -------------------------------------------------------
#                    2D operations
# -------------------------------------------------------
class Union2D(FlattenerOp2D):
    def __init__(self, flatten: bool = True):
        """
        `See. <https://github.com/arnholm/xcsg/wiki/union2d>`__

        **examples:**
         * res = Union2D()(obj1, obj2, obj3)
         * res = obj1 + obj2 + obj3

        :param flatten: if True, multiple depth union topologies are flattened to one level union if possible
        """
        super().__init__('union2d', flatten)


class Diff2D(Obj2D):
    def __init__(self):
        """
        `See. <https://github.com/arnholm/xcsg/wiki/difference2d>`__

        **examples:**
         * res = Diff2D()(obj, hole1, hole2)
         * res = obj - hole1 - hole2

        alias: Difference2D
        """
        super().__init__('difference2d', MoreChildren(Obj2D))


Difference2D = Diff2D


class Intersection2D(Obj2D):

    def __init__(self):
        """
        `See. <https://github.com/arnholm/xcsg/wiki/intersection2d>`__

        **example:** res = Intersection2D()(obj1, obj2, obj3)

        alias: Sect2D
        """
        super().__init__('intersection2d', MoreChildren(Obj2D))


Sect2D = Intersection2D


class Fill2D(Obj2D):

    def __init__(self):
        """
        `See. <https://github.com/arnholm/xcsg/wiki/fill2d>`__
        """
        super().__init__('fill2d', OneChild(Obj2D))


class Hull2D(Obj2D):

    def __init__(self):
        """
        `See. <https://github.com/arnholm/xcsg/wiki/hull2d>`__

        **example:** res = Hull2D()(rectangle, circle)
        """
        super().__init__('hull2d', MoreChildren(Obj2D))


class Offset2D(Obj2D):

    def __init__(self, delta: float, round: bool, chamfer: bool = False):
        """
         `See. <https://github.com/arnholm/xcsg/wiki/offset2d>`__

         **example:** res = Offset2D(delta=1, round=True)(obj)

        :param delta: offset distance
        :param round: rounded corners
        :param chamfer: chamfer corners
        """
        super().__init__('offset2d', OneChild(Obj2D), delta=delta, round=round, chamfer=chamfer)


class Minkowski2D(Obj2D):

    def __init__(self):
        """
        `See. <https://github.com/arnholm/xcsg/wiki/minkowski2d>`__

        **example:** res = Minkowski2D()(rectangle, circle)
        """
        super().__init__('minkowski2d', TwoChildren(Obj2D))


# -------------------------------------------------------
#                3D to 2D operations
# -------------------------------------------------------
class Projection2D(Obj2D):

    def __init__(self):
        """
        Projects 3D shape into the XY-plane, resulting a 2D shape.
        `See. <https://github.com/arnholm/xcsg/wiki/projection2d>`__

        **example:** res = Projection2D()(obj1 + obj2)
        """
        super().__init__('projection2d', OneChild(Obj3D))


# -------------------------------------------------------
#                    3D objects
# -------------------------------------------------------
class Cone(Obj3D):

    def __init__(self, r1: float, r2: float, h: float, center: bool = False):
        """
        `See. <https://github.com/arnholm/xcsg/wiki/cone>`__

        :param r1: radius of the bottom circle section
        :param r2: radius of top circle section
        :param h: height of cone
        :param center: center on origin
        """
        super().__init__('cone', r1=r1, r2=r2, h=h, center=center)


class Cube(Obj3D):

    def __init__(self, size: float, center: bool = False):
        """
        `See. <https://github.com/arnholm/xcsg/wiki/cube>`__

        :param size: extent in x, y and z
        :param center: center on origin
        """
        super().__init__('cube', size=size, center=center)


class Cuboid(Obj3D):

    def __init__(self, dx: float, dy: float, dz: float, center: bool = False):
        """
        `See. <https://github.com/arnholm/xcsg/wiki/cuboid>`__

        alias: **Box**

        :param dx: extent in x
        :param dy: extent in y
        :param dz: Extent in z
        :param center: center on origin
        """
        super().__init__('cuboid', dx=dx, dy=dy, dz=dz, center=center)


Box = Cuboid


class Cylinder(Obj3D):

    def __init__(self, r: float, h: float, center: bool = False):
        """
        `See. <https://github.com/arnholm/xcsg/wiki/cylinder>`__

        :param r: radius
        :param h: height
        :param center: center on origin
        """
        super().__init__('cylinder', r=r, h=h, center=center)


class Polyhedron(Obj3D):

    def __init__(self, vertices: List[glm.vec3], faces: List[Tuple] = None):
        """
        `See. <https://github.com/arnholm/xcsg/wiki/polyhedron>`__

        :param vertices:
        :param faces: list of vertex index tuples, can be None to create a convex hull of vertices
        """
        super().__init__('polyhedron')
        self.vertices, self.faces = vertices, faces

    def _get_child_nodes(self):
        verts = mk_node('vertices')
        for v in self.vertices:
            verts.append(mk_node('vertex', x=v.x, y=v.y, z=v.z))
        res = [verts]
        if self.faces is not None:
            faces = mk_node('faces')
            for f in self.faces:
                face = mk_node('face')
                faces.append(face)
                for idx in f:
                    face.append(mk_node('fv', index=idx))
            res += [faces]
        return res


class Sphere(Obj3D):

    def __init__(self, r: float):
        """
        `See. <https://github.com/arnholm/xcsg/wiki/sphere>`__

        :param r: radius
        """
        super().__init__('sphere', r=r)


# -------------------------------------------------------
#                2D to 3D operations
# -------------------------------------------------------
class LinearExtrude(Obj3D):

    def __init__(self, dz: float):
        """
        `See. <https://github.com/arnholm/xcsg/wiki/linear_extrude>`__

        **example:** res = LinearExtrude(dz=1)(polygon)

        :param dz: extrude distance on Z axis
        """
        super().__init__('linear_extrude', OneChild(Obj2D), dz=dz)


class RotateExtrude(Obj3D):

    def __init__(self, angle: float, pitch: float = 0):
        """
        `See. <https://github.com/arnholm/xcsg/wiki/rotate_extrude>`__

        **example:** res = RotateExtrude(angle=math.pi)(polygon)

        :param angle: rotation angle [radians] around Y
        :param pitch: offset in Y per revolution
        """
        super().__init__('rotate_extrude', OneChild(Obj2D), angle=angle, pitch=pitch)


class TransformExtrude(Obj3D):

    def __init__(self):
        """
        Extrudes a 2D shape into an other to form a solid.

        **example:** TransformExtrude()(Square(size=60, center=True), tr([0, 0, 50], Circle(r=30))))

        `See. <https://github.com/arnholm/xcsg/wiki/transform_extrude>`__
        """
        super().__init__('transform_extrude', TwoChildren(Obj2D))


class Sweep(Obj3D):

    def __init__(self, spline_path: List[Tuple[glm.vec3, glm.vec3]]):
        """
        Extrude 2D shape around a spline to form a solid.

        `See. <https://github.com/arnholm/xcsg/wiki/sweep>`__

        :param spline_path: [(p: vec3, v: vec3), ...]
        """
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
    def __init__(self, flatten: bool = True):
        """
        `See. <https://github.com/arnholm/xcsg/wiki/union3d>`__

        **examples:**
         * res = Union3D()(obj1, obj2, obj3)
         * res = obj1 + obj2 + obj3

        :param flatten: if True, multiple depth union topologies are flattened to one level union if possible
        """
        super().__init__('union3d', flatten)


class Diff3D(Obj3D):
    def __init__(self):
        """
        `See. <https://github.com/arnholm/xcsg/wiki/difference3d>`__

        **examples:**
         * res = Diff3D()(obj, hole1, hole2)
         * res = obj - hole1 - hole2

        alias: Difference3D
        """
        super().__init__('difference3d',  MoreChildren(Obj3D))


Difference3D = Diff3D


class Intersection3D(Obj3D):
    def __init__(self):
        """
        `See. <https://github.com/arnholm/xcsg/wiki/intersection3d>`__

        **example:** res = Intersection3D()(obj1, obj2, obj3)

        alias: Sect3D
        """
        super().__init__('intersection3d', MoreChildren(Obj3D))


Sect3D = Intersection3D


class Hull3D(Obj3D):
    def __init__(self):
        """
        `See. <https://github.com/arnholm/xcsg/wiki/hull3d>`__

        **example:** res = Hull3D()(box, sphere)
        """
        super().__init__('hull3d', MoreChildren(Obj3D))


class Minkowski3D(Obj3D):
    def __init__(self):
        """
        `See. <https://github.com/arnholm/xcsg/wiki/minkowski3d>`__

        **example:** res = Minkowski3D()(cube, sphere)
        """
        super().__init__('minkowski3d', MoreChildren(Obj3D))


def to_vec2(v: Union[List, Tuple, glm.vec1, glm.vec2]) -> glm.vec2:
    if isinstance(v, (list, tuple, glm.vec1)):
        if len(v) < 1:
            v = list(v) + [0 for _ in range(1 - len(v))]
            return glm.vec2(v)
        return glm.vec2(v[:2])
    elif not isinstance(v, glm.vec2):
        return glm.vec2(v)
    return v


def to_vec3(v: Union[List, Tuple, glm.vec1, glm.vec2, glm.vec3]) -> glm.vec3:
    if isinstance(v, (list, tuple, glm.vec1, glm.vec2)):
        if len(v) < 3:
            v = list(v) + [0 for _ in range(3 - len(v))]
            return glm.vec3(v)
        return glm.vec3(v)
    elif not isinstance(v, glm.vec3):
        return glm.vec3(v)
    return v


def to_vec4(v: Union[List, Tuple, glm.vec1, glm.vec2, glm.vec3, glm.vec4]) -> glm.vec4:
    if isinstance(v, glm.vec4):
        return v
    if isinstance(v, (list, tuple, glm.vec3, glm.vec2)):
        if len(v) < 4:
            return glm.vec4(to_vec3(v), 0)
        return glm.vec4(v)
    assert False


def translate(v: glm.vec3, obj: Obj) -> Obj:
    """
    Translates a 2D or 3D object.

    **aliases:** tr, move_to

    :param v: vector of translation
    :param obj: the object
    :return: the new translated object
    """
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


def rotate(ang: float, axis: glm.vec3, obj: Obj) -> Obj:
    """
    Rotates a 2D or 3D object around an axis.

    :param ang: angle of rotation in radians
    :param axis: the rotation axis
    :param obj: the object
    :return: the new rotated object
    """
    obj = obj.copy()
    rm = glm.mat4x4()
    rm = glm.rotate(rm, ang, axis)
    obj.model_matrix = rm * obj.model_matrix
    return obj


def scale(v: Union[List, Tuple, glm.vec3], obj: Obj) -> Obj:
    """
    Scales an object along the X,Y,Z axes.

    :param v: scale vector
    :param obj: the object
    :return: the new scaled object
    """
    obj = obj.copy()
    # set missing dimensions to 1
    if isinstance(v, (list, tuple)) and len(v) < 3:
        v = list(v) + [1 for _ in range(3 - len(v))]
    obj.model_matrix = glm.scale(obj.model_matrix, to_vec3(v))
    return obj


def mirror_vector(normal_unit: glm.vec3, v: glm.vec3) -> glm.vec3:
    """
    Mirrors a vector.

    :param normal_unit: unit length normal vector of the mirroring plane
    :param v: vector to be mirrored
    :return: the mirrored vector
    """
    prj_len = glm.dot(normal_unit, v)
    scaled_axis = 2 * prj_len * normal_unit
    return v - scaled_axis


def mirror(normal: glm.vec3, obj: Obj) -> Obj:
    """
    Mirrors an object to a plane. The plane is residing on the origin.

    :param normal: mirror plane's normal vector
    :param obj: the object
    :return: the new mirrored object
    """
    obj = obj.copy()
    normal_unit = glm.normalize(to_vec3(normal))
    mm = obj.model_matrix
    i, j, k, l = [mirror_vector(normal_unit, mm[i].xyz) for i in range(4)]
    mm[0], mm[1], mm[2] = [glm.vec4(v, 0) for v in (i, j, k)]
    mm[3] = glm.vec4(l, 1)
    return obj


def to_xml(obj: Obj3D, secant_tolerance: float = 0.01) -> etree.Element:
    """
    Dumps the object into an lxml DOM tree.

    :param obj: the object
    :param secant_tolerance: precision of curved edges or surfaces
    :return: the root DOM element
    """
    assert isinstance(obj, Obj3D)
    pre_process(obj)
    root = mk_node('xcsg', version='1.0', secant_tolerance=secant_tolerance)
    root.append(obj.to_element())
    return root


def save(file_path: str, obj: Obj, secant_tolerance: float = 0.01) -> None:
    """
    Saves the object into a .xcsg file.

    :param file_path:
    :param obj:
    :param secant_tolerance: precision of curved edges or surfaces
    """
    root = to_xml(obj, secant_tolerance=secant_tolerance)
    with open(file_path, 'w') as f:
        f.write(etree.tostring(root, encoding='utf-8', pretty_print=True).decode())
