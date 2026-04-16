# `blip`

When the object is created or deleted, it will animate in/out of the scene instead of appearing/disappearing instantly. Must have a geometric mesh.

This is the schema for Blip Effect, the properties of object `blip`.

**Used by:** [ARENAUI Button Panel](arenaui-button-panel), [ARENAUI Card Panel](arenaui-card), [ARENAUI Prompt](arenaui-prompt), [Box](box), [Capsule](capsule), [Circle](circle), [Cone](cone), [Cube (deprecated; don't use)](cube), [Cylinder](cylinder), [Dodecahedron](dodecahedron), [Entity (generic object)](entity), [Gaussian Splat](gaussian_splatting), [GLTF Model](gltf-model), [Icosahedron](icosahedron), [Image](image), [Light](light), [OBJ Model](obj-model), [Octahedron](octahedron), [PCD Model](pcd-model), [Plane](plane), [Ring](ring), [Rounded Box](roundedbox), [Sphere](sphere), [Tetrahedron](tetrahedron), [Three.js Scene](threejs-scene), [Torus](torus), [Torus Knot](torusKnot), [Triangle](triangle), [URDF Model](urdf-model), [Videosphere](videosphere)

## Blip Effect Attributes

| Attribute | Type | Default | Description | Required |
| :--- | :--- | :--- | :--- | :--- |
| **blipin** | boolean | `True` | Animate in on create, set false to disable. | Yes |
| **blipout** | boolean | `True` | Animate out on delete, set false to disable. | Yes |
| **geometry** | string; One of: `['rect', 'disk', 'ring']` | `'rect'` | Geometry of the blipout plane. | Yes |
| **planes** | string; One of: `['both', 'top', 'bottom']` | `'both'` | Which which clipping planes to use for effect. A top plane clips above it, bottom clips below it. | Yes |
| **duration** | number | `750` | Animation duration in milliseconds. | Yes |
| **applyDescendants** | boolean | `False` | Apply blipout effect to include all descendents. Does not work for blipin. | No |

