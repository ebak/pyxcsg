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
from copy import deepcopy

from xcsg.common import IDENTITY


def mk_node(name, **attrs):
    attr_dict = {}
    for k, v in attrs.items():
        if isinstance(v, bool):
            v = 'true' if v else 'false'
        else:
            v = str(v)
        attr_dict[k] = v
    return etree.Element(name, attr_dict)


class ChildValidator:

    def __init__(self, child_type, min_cnt=None, max_cnt=None):
        self.child_type, self.min_cnt, self.max_cnt = child_type, min_cnt, max_cnt

    def validate(self, *objs):
        cnt = len(objs)
        if self.min_cnt is not None:
            assert cnt >= self.min_cnt
        if self.max_cnt is not None:
            assert cnt <= self.max_cnt
        for o in objs:
            assert isinstance(o, self.child_type), f'type(o): {type(o)} != child_type: {self.child_type}\no: {o}'


class OneChild(ChildValidator):
    def __init__(self, child_type):
        super().__init__(child_type, min_cnt=1, max_cnt=1)


class TwoChildren(ChildValidator):
    def __init__(self, child_type):
        super().__init__(child_type, min_cnt=2, max_cnt=2)


class Obj:

    def __init__(self, node_name, child_validator=None, **attrs):
        self.node_name, self.child_validator, self.attrs = node_name, child_validator, attrs
        self.objs = []
        self.model_matrix = glm.identity(glm.mat4x4)

    def __call__(self, *objs):
        assert self.child_validator is not None
        self.child_validator.validate(*objs)
        self.objs = objs
        return self

    def copy(self):
        # shallow copy child objects only
        objs = self.objs
        self.objs = None
        clone = deepcopy(self)
        clone.objs = self.objs = objs
        return clone

    def deep_copy(self):
        return deepcopy(self)

    def to_element(self):
        e = mk_node(self.node_name, **self.attrs)
        # if the matrix is identity, don't write it
        mm = self.model_matrix
        if mm != IDENTITY:
            m = mk_node('tmatrix')
            for i, j, k, l in zip(mm[0], mm[1], mm[2], mm[3]):
                m.append(mk_node('trow', c0=i, c1=j, c2=k, c3=l))
            e.append(m)
        for co in self.objs:
            e.append(co.to_element())
        for c in self._get_child_nodes():
            e.append(c)
        return e

    def _get_child_nodes(self):
        return []


class MoreChildren(ChildValidator):
    def __init__(self, child_type):
        super().__init__(child_type, min_cnt=1, max_cnt=None)


class Obj2D(Obj):

    def __init__(self, node_name, child_validator=None, **attrs):
        super().__init__(node_name, child_validator, **attrs)

    def __add__(self, o):
        from .api import Union2D    # cyclic import
        return Union2D()(self, o)

    def __sub__(self, o):
        from .api import Diff2D    # cyclic import
        return Diff2D()(self, o)


def flatten(parent_obj, *objs):
    flattened_objs = []
    for o in objs:
        if isinstance(o, type(parent_obj)) and parent_obj.model_matrix == o.model_matrix:
            # intend to flat nested unions and diffs
            flattened_objs += o.objs
        else:
            flattened_objs.append(o)
    return flattened_objs


class FlattenerOp2D(Obj2D):

    def __init__(self, node_name, flatten=True, **attrs):
        super().__init__(node_name, MoreChildren(Obj2D), **attrs)
        self.flatten = flatten

    def __call__(self, *objs):
        self.child_validator.validate(*objs)
        self.objs = flatten(self, *objs) if self.flatten else objs
        return self


class Obj3D(Obj):

    def __init__(self, node_name, child_validator=None, **attrs):
        super().__init__(node_name, child_validator, **attrs)

    def __add__(self, o):
        from .api import Union3D    # cyclic import
        return Union3D()(self, o)

    def __sub__(self, o):
        from .api import Diff3D    # cyclic import
        return Diff3D()(self, o)


class FlattenerOp3D(Obj3D):

    def __init__(self, node_name, flatten=True, **attrs):
        super().__init__(node_name, MoreChildren(Obj3D), **attrs)
        self.flatten = flatten

    def __call__(self, *objs):
        self.child_validator.validate(*objs)
        self.objs = flatten(self, *objs) if self.flatten else objs
        return self


def tree_struct(op_cls, parts, depth=0):
    if len(parts) <= 3:
        # print(f'{depth}. leaf_part: {parts[0]}, objs: {parts[0].objs}')
        return parts
    new_parts = []
    odd = len(parts) & 1 == 1
    for i in range(int(len(parts) / 2)):
        idx = 2 * i
        nidx = idx + 1
        p0, p1 = parts[idx], parts[nidx]
        part = (
            op_cls(flatten=False)(p0, p1, parts[nidx + 1])
            if odd and nidx == len(parts) - 2 else
            op_cls(flatten=False)(p0, p1))
        new_parts.append(part)
        # print(f'{depth}. new_parts: {new_parts}')
    return tree_struct(op_cls, new_parts, depth + 1)


def tree_children(op):
    op.objs = tree_struct(type(op), op.objs)


def pre_process(obj, depth=0):
    from xcsg.api import Union2D, Union3D     # cyclic import
    if isinstance(obj, (Union2D, Union3D)):
        tree_children(obj)
    for o in obj.objs:
        pre_process(o, depth + 1)
