# `video-control`

Adds a video to an entity and controls its playback.

This is the schema for Video, the properties of object `video-control`.

**Used by:** [ARENAUI Button Panel](arenaui-button-panel), [ARENAUI Card Panel](arenaui-card), [ARENAUI Prompt](arenaui-prompt), [Box](box), [Capsule](capsule), [Circle](circle), [Cone](cone), [Cube (deprecated; don't use)](cube), [Cylinder](cylinder), [Dodecahedron](dodecahedron), [Entity (generic object)](entity), [Gaussian Splat](gaussian_splatting), [GLTF Model](gltf-model), [Icosahedron](icosahedron), [Image](image), [Light](light), [OBJ Model](obj-model), [Octahedron](octahedron), [PCD Model](pcd-model), [Plane](plane), [Ring](ring), [Rounded Box](roundedbox), [Sphere](sphere), [Tetrahedron](tetrahedron), [Three.js Scene](threejs-scene), [Torus](torus), [Torus Knot](torusKnot), [Triangle](triangle), [URDF Model](urdf-model), [Videosphere](videosphere)

## Video Attributes

| Attribute | Type | Default | Description | Required |
| :--- | :--- | :--- | :--- | :--- |
| **frame_object** | string |  | URL of a thumbnail image, e.g. 'store/users/wiselab/images/conix-face-white.jpg'. | Yes |
| **video_object** | string |  | Name of object where to put the video, e.g. 'square_vid6'. | Yes |
| **video_path** | string |  | URL of the video file, e.g. 'store/users/wiselab/videos/kungfu.mp4'. | Yes |
| **anyone_clicks** | boolean | `True` | Responds to clicks from any user. | No |
| **video_loop** | boolean | `True` | Video automatically loops. | No |
| **autoplay** | boolean | `False` | Video starts playing automatically. | No |
| **volume** | number | `1` | Video sound volume. | No |
| **cleanup** | boolean | `True` | Automatically remove HTML5 video and img assets from DOM on object removal. | No |

