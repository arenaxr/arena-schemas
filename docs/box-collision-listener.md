# `box-collision-listener`

Listen for bounding-box collisions with user camera and hands. Must be applied to an object or model with geometric mesh. Collisions are determined by course bounding-box overlaps.

This is the schema for Box Collision Listener, the properties of object `box-collision-listener`.

**Used by:** [ARENAUI Button Panel](arenaui-button-panel), [ARENAUI Card Panel](arenaui-card), [ARENAUI Prompt](arenaui-prompt), [Box](box), [Capsule](capsule), [Circle](circle), [Cone](cone), [Cube (deprecated; don't use)](cube), [Cylinder](cylinder), [Dodecahedron](dodecahedron), [Entity (generic object)](entity), [Gaussian Splat](gaussian_splatting), [GLTF Model](gltf-model), [Icosahedron](icosahedron), [Image](image), [Light](light), [OBJ Model](obj-model), [Octahedron](octahedron), [PCD Model](pcd-model), [Plane](plane), [Ring](ring), [Rounded Box](roundedbox), [Sphere](sphere), [Tetrahedron](tetrahedron), [Three.js Scene](threejs-scene), [Torus](torus), [Torus Knot](torusKnot), [Triangle](triangle), [URDF Model](urdf-model), [Videosphere](videosphere)

## Box Collision Listener Attributes

| Attribute | Type | Default | Description | Required |
| :--- | :--- | :--- | :--- | :--- |
| **enabled** | boolean | `True` | Publish detections, set `false` to disable. | No |
| **dynamic** | boolean | `False` | Set true for a moving object, which should have its bounding box recalculated regularly to determine proper collision. | Yes |

