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
