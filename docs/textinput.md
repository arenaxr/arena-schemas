# `textinput`

Opens an HTML prompt when clicked. Sends text input as an event on MQTT. Requires `click-listener` attribute.

This is the schema for Text Input, the properties of object `textinput`.

**Used by:** [ARENAUI Button Panel](arenaui-button-panel), [ARENAUI Card Panel](arenaui-card), [ARENAUI Prompt](arenaui-prompt), [Box](box), [Capsule](capsule), [Circle](circle), [Cone](cone), [Cube (deprecated; don't use)](cube), [Cylinder](cylinder), [Dodecahedron](dodecahedron), [Entity (generic object)](entity), [Gaussian Splat](gaussian_splatting), [GLTF Model](gltf-model), [Icosahedron](icosahedron), [Image](image), [Light](light), [OBJ Model](obj-model), [Octahedron](octahedron), [PCD Model](pcd-model), [Plane](plane), [Ring](ring), [Rounded Box](roundedbox), [Sphere](sphere), [Tetrahedron](tetrahedron), [Three.js Scene](threejs-scene), [Torus](torus), [Torus Knot](torusKnot), [Triangle](triangle), [URDF Model](urdf-model), [Videosphere](videosphere)

## Text Input Attributes

| Attribute | Type | Default | Description | Required |
| :--- | :--- | :--- | :--- | :--- |
| **on** | string; One of: `['mousedown', 'mouseup', 'mouseenter', 'mouseleave', 'triggerdown', 'triggerup', 'gripdown', 'gripup', 'menudown', 'menuup', 'systemdown', 'systemup', 'trackpaddown', 'trackpadup']` | `'mousedown'` | A case-sensitive string representing the event type to listen for. See <a href='https://developer.mozilla.org/en-US/docs/Web/Events'>Web Events</a> | Yes |
| **title** | string | `''` | The prompt title (optional). | Yes |
| **label** | string | `''` | Label for input (max 140 characters, optional). | No |
| **placeholder** | string | `''` | Text input placeholder (optional). | No |
| **inputType** | string; One of: `['text', 'email', 'password', 'number', 'tel', 'range', 'textarea', 'url', 'select', 'radio', 'checkbox', 'date', 'datetime-local', 'time', 'week', 'month']` | `'text'` | Type of HTML form input | No |
| **inputValue** | string | `''` | Input field initial value. Select type will be selected value, for checkbox will be checked state | No |
| **inputOptions** | string[] | `[]` | Array of options for select or radio input types | No |

