# `physx-material`

Controls physics properties for individual shapes or rigid bodies. Can be set on an entity with physx-body or on shapes contained within it. Requires `scene-options: physics`.

This is the schema for PhysX Material, the properties of object `physx-material`.

**Used by:** [ARENAUI Button Panel](arenaui-button-panel), [ARENAUI Card Panel](arenaui-card), [ARENAUI Prompt](arenaui-prompt), [Box](box), [Capsule](capsule), [Circle](circle), [Cone](cone), [Cube (deprecated; don't use)](cube), [Cylinder](cylinder), [Dodecahedron](dodecahedron), [Entity (generic object)](entity), [Gaussian Splat](gaussian_splatting), [GLTF Model](gltf-model), [Icosahedron](icosahedron), [Image](image), [Light](light), [OBJ Model](obj-model), [Octahedron](octahedron), [PCD Model](pcd-model), [Plane](plane), [Ring](ring), [Rounded Box](roundedbox), [Sphere](sphere), [Tetrahedron](tetrahedron), [Three.js Scene](threejs-scene), [Torus](torus), [Torus Knot](torusKnot), [Triangle](triangle), [URDF Model](urdf-model), [Videosphere](videosphere)

## PhysX Material Attributes

| Attribute | Type | Default | Description | Required |
| :--- | :--- | :--- | :--- | :--- |
| **staticFriction** | number | `0.2` | Static friction applied when objects are not moving relative to each other. | No |
| **dynamicFriction** | number | `0.2` | Dynamic friction applied when objects are moving relative to each other. | No |
| **restitution** | number | `0.2` | Restitution, or 'bounciness' of the material. | No |
| **density** | number |  | Density for the shape. If specified for all shapes in a rigid body, mass properties will be automatically calculated based on densities. | No |
| **collisionLayers** | number[] | `[1]` | Which collision layers this shape is present on. | No |
| **collidesWithLayers** | number[] | `[1, 2, 3, 4]` | Array containing all layers that this shape should collide with. | No |
| **collisionGroup** | number | `0` | If greater than 0, this shape will not collide with any other shape with the same collisionGroup value. | No |
| **contactOffset** | string |  | If >= 0, sets the PhysX contact offset, indicating how far away from the shape simulation contact events should begin. | No |
| **restOffset** | string |  | If >= 0, sets the PhysX rest offset. | No |

