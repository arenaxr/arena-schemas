# `goto-landmark`

Teleports user to the landmark with the given name. Requires `click-listener` attribute.

This is the schema for Goto Landmark, the properties of object `goto-landmark`.

**Used by:** [ARENAUI Button Panel](arenaui-button-panel), [ARENAUI Card Panel](arenaui-card), [ARENAUI Prompt](arenaui-prompt), [Box](box), [Capsule](capsule), [Circle](circle), [Cone](cone), [Cube (deprecated; don't use)](cube), [Cylinder](cylinder), [Dodecahedron](dodecahedron), [Entity (generic object)](entity), [Gaussian Splat](gaussian_splatting), [GLTF Model](gltf-model), [Icosahedron](icosahedron), [Image](image), [Light](light), [OBJ Model](obj-model), [Octahedron](octahedron), [PCD Model](pcd-model), [Plane](plane), [Ring](ring), [Rounded Box](roundedbox), [Sphere](sphere), [Tetrahedron](tetrahedron), [Three.js Scene](threejs-scene), [Torus](torus), [Torus Knot](torusKnot), [Triangle](triangle), [URDF Model](urdf-model), [Videosphere](videosphere)

## Goto Landmark Attributes

| Attribute | Type | Default | Description | Required |
| :--- | :--- | :--- | :--- | :--- |
| **on** | string; One of: `['mousedown', 'mouseup']` | `'mousedown'` | Event to listen 'on'. | Yes |
| **landmark** | string | `''` | Id of landmark to teleport to. | Yes |

