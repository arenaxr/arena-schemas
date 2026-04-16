# `model-container`

Overrides absolute size for a 3D model. The model can be a glTF, glb, obj, or any other supported format. The model will be rescaled to fit to the sizes specified for each axes.

This is the schema for Model Container, the properties of object `model-container`.

**Used by:** [ARENAUI Button Panel](arenaui-button-panel), [ARENAUI Card Panel](arenaui-card), [ARENAUI Prompt](arenaui-prompt), [Box](box), [Capsule](capsule), [Circle](circle), [Cone](cone), [Cube (deprecated; don't use)](cube), [Cylinder](cylinder), [Dodecahedron](dodecahedron), [Entity (generic object)](entity), [Gaussian Splat](gaussian_splatting), [GLTF Model](gltf-model), [Icosahedron](icosahedron), [Image](image), [Light](light), [OBJ Model](obj-model), [Octahedron](octahedron), [PCD Model](pcd-model), [Plane](plane), [Ring](ring), [Rounded Box](roundedbox), [Sphere](sphere), [Tetrahedron](tetrahedron), [Three.js Scene](threejs-scene), [Torus](torus), [Torus Knot](torusKnot), [Triangle](triangle), [URDF Model](urdf-model), [Videosphere](videosphere)

## Model Container Attributes

| Attribute | Type | Default | Description | Required |
| :--- | :--- | :--- | :--- | :--- |
| **x** | number | `1` | Size of the model in the x-axis. | Yes |
| **y** | number | `1` | Size of the model in the y-axis. | Yes |
| **z** | number | `1` | Size of the model in the z-axis. | Yes |
| **uniform** | boolean | `True` | Whether to scale the model uniformly. | Yes |

