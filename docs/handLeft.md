# `handLeft`

Hand is the (left or right) hand metadata pose and controller type of the user avatar.

This is the schema for Hand, the properties of wire object type `handLeft`.


All wire objects have a set of basic [ARENA Message](arena-message) envelope attributes: `{object_id, action, type, persist, data}`.
- The `type` attribute must be set to `"object"` for this wire object.
- The `data` attribute defines the `handLeft` object-specific attributes listed below.


### Hand Properties

| Attribute | Type | Default | Description | Required |
| :--- | :--- | :--- | :--- | :--- |
| **object_type** | string; One of: `['handLeft', 'handRight']` |  | 3D object type. | Yes |
| **url** | string | `'static/models/hands/valve_index_left.gltf'` | Path to user avatar hand model. | Yes |
| **dep** | string | `''` | Camera object_id this hand belongs to. | Yes |


### Entity Properties

| Attribute | Type | Default | Description | Required |
| :--- | :--- | :--- | :--- | :--- |
| **parent** | string |  | Parent's object_id. Child objects inherit attributes of their parent, for example scale and translation. | No |
| **position** | [Position](position) |  | 3D object position. | Yes |
| **rotation** | [Rotation](rotation) |  | 3D object rotation in quaternion representation; Right-handed coordinate system. Euler degrees are deprecated in wire message format. | Yes |
| **scale** | [Scale](scale) |  | 3D object scale. | No |
| **visible** | boolean | `True` | Whether object is visible. Property is inherited. | No |

