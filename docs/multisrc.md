# `multisrc`

Define multiple visual sources applied to an object. Requires `material` attribute.

This is the schema for Multi Source, the properties of object `multisrc`.

**Used by:** [Box](box), [Capsule](capsule), [Circle](circle), [Cone](cone), [Cube (deprecated; don't use)](cube), [Cylinder](cylinder), [Dodecahedron](dodecahedron), [Icosahedron](icosahedron), [Image](image), [OBJ Model](obj-model), [Octahedron](octahedron), [Plane](plane), [Ring](ring), [Rounded Box](roundedbox), [Sphere](sphere), [Tetrahedron](tetrahedron), [Torus](torus), [Torus Knot](torusKnot), [Triangle](triangle), [Videosphere](videosphere)

## Multi Source Attributes

| Attribute | Type | Default | Description | Required |
| :--- | :--- | :--- | :--- | :--- |
| **srcs** | string |  | A comma-delimited list if URIs, e.g. 'side1.png, side2.png, side3.png, side4.png, side5.png, side6.png' (required). | Yes |
| **srcspath** | string |  | URI, relative or full path of a directory containing srcs, e.g. 'store/users/wiselab/images/dice/' (required). | Yes |

