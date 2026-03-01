# `handRight`

Hand is the (left or right) hand metadata pose and controller type of the user avatar.

This is the schema for Hand, the properties of wire object type `handRight`.

All wire objects have a set of basic attributes `{object_id, action, type, persist, data}`. The `data` attribute defines the object-specific attributes

## Hand Attributes

| Attribute | Type | Default | Description | Required |
| :--- | :--- | :--- | :--- | :--- |
| **data** | Hand data | | Hand object data properties as defined below | Yes |
| **url** | string | `'static/models/hands/valve_index_left.gltf'` | Path to user avatar hand model. | Yes |
| **dep** | string | `''` | Camera object_id this hand belongs to. | Yes |
| **parent** | string |  | Parent's object_id. Child objects inherit attributes of their parent, for example scale and translation. | No |
| **position** | [Position](position) |  | 3D object position. | Yes |
| **rotation** | [Rotation](rotation) |  | 3D object rotation in quaternion representation; Right-handed coordinate system. Euler degrees are deprecated in wire message format. | Yes |
| **scale** | [Scale](scale) |  | 3D object scale. | No |
| **visible** | boolean | `True` | Whether object is visible. Property is inherited. | No |

