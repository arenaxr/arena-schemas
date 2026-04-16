# `goto-url`

Load new URL when object is clicked. Requires `click-listener` attribute.

This is the schema for Goto URL, the properties of object `goto-url`.

**Used by:** [ARENAUI Button Panel](arenaui-button-panel), [ARENAUI Card Panel](arenaui-card), [ARENAUI Prompt](arenaui-prompt), [Box](box), [Capsule](capsule), [Circle](circle), [Cone](cone), [Cube (deprecated; don't use)](cube), [Cylinder](cylinder), [Dodecahedron](dodecahedron), [Entity (generic object)](entity), [Gaussian Splat](gaussian_splatting), [GLTF Model](gltf-model), [Icosahedron](icosahedron), [Image](image), [Light](light), [OBJ Model](obj-model), [Octahedron](octahedron), [PCD Model](pcd-model), [Plane](plane), [Ring](ring), [Rounded Box](roundedbox), [Sphere](sphere), [Tetrahedron](tetrahedron), [Three.js Scene](threejs-scene), [Torus](torus), [Torus Knot](torusKnot), [Triangle](triangle), [URDF Model](urdf-model), [Videosphere](videosphere)

## Goto URL Attributes

| Attribute | Type | Default | Description | Required |
| :--- | :--- | :--- | :--- | :--- |
| **dest** | string; One of: `['popup', 'newtab', 'sametab']` | `'sametab'` | Where to open the URL. | Yes |
| **on** | string; One of: `['mousedown', 'mouseup']` | `'mousedown'` | A case-sensitive string representing the event type to listen for. See <a href='https://developer.mozilla.org/en-US/docs/Web/Events'>Web Events</a>. | Yes |
| **url** | string | `''` | The destination url, e.g. https://example.com. | Yes |

