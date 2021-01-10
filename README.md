### Very basic `.xcsg` generator for `Python`.

Usable together with the [xcsg](https://github.com/arnholm/xcsg) and [AngelCAD](https://github.com/arnholm/angelcad)
tools, `AngelCAD` is not mandatory, but good to have.

It is something like [SolidPython](https://github.com/SolidCode/SolidPython) for
[OpenSCAD](https://github.com/openscad/openscad).

Work is in progress, there is no documentation yet and it is probably quite buggy.

See `samples.py` for usage examples, see `api.py` for the available wrappers, and take a look at the [xcsg wiki](https://github.com/arnholm/xcsg/wiki).

#### Usage example
`example.py`:
```
import math

from xcsg import rotate, X_AXIS, Y_AXIS, Sect3D, Cube, Sphere, Cylinder, save

cylinder = Cylinder(r=17, h=50, center=True)
shape = Sect3D()(
    Cube(size=45, center=True),
    Sphere(r=30))
shape -= (
    cylinder +
    rotate(ang=math.radians(90), axis=X_AXIS, obj=cylinder) +
    rotate(ang=math.radians(90), axis=Y_AXIS, obj=cylinder))

save('example.xcsg', shape)
```
```
$ python example.py
$ xcsg --obj example.xcsg
...
$ angelview example.obj
```
![Alt text](AngelView.jpg?raw=true "Title")