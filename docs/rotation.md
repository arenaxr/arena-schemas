# `rotation`

3D object rotation in quaternion representation; Right-handed coordinate system. Euler degrees are deprecated in wire message format.

This is the schema for Rotation, the properties of object `rotation`.

**Used by:** [ARENAUI Button Panel](arenaui-button-panel), [ARENAUI Card Panel](arenaui-card), [ARENAUI Prompt](arenaui-prompt), [Box](box), [Camera Override](camera), [Camera Override Data](camera-override), [Capsule](capsule), [Circle](circle), [Cone](cone), [Cube (deprecated; don't use)](cube), [Cylinder](cylinder), [Dodecahedron](dodecahedron), [Entity (generic object)](entity), [Gaussian Splat](gaussian_splatting), [GLTF Model](gltf-model), [Hand](handLeft), [Hand](handRight), [Icosahedron](icosahedron), [Image](image), [Light](light), [Line](line), [Camera Override](look-at), [OBJ Model](obj-model), [Ocean](ocean), [Octahedron](octahedron), [PCD Model](pcd-model), [Plane](plane), [Ring](ring), [Rounded Box](roundedbox), [Sphere](sphere), [Camera Override](teleport-to-landmark), [Tetrahedron](tetrahedron), [Text](text), [Thickline](thickline), [Three.js Scene](threejs-scene), [Torus](torus), [Torus Knot](torusKnot), [Triangle](triangle), [URDF Model](urdf-model), [Videosphere](videosphere)

## Rotation Attributes

| Attribute | Type | Default | Description | Required |
| :--- | :--- | :--- | :--- | :--- |
| **w** | number | `1` | w | Yes |
| **x** | number | `0` | x | Yes |
| **y** | number | `0` | y | Yes |
| **z** | number | `0` | z | Yes |

