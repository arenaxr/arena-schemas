# `line`

Draw a line.

This is the schema for Line, the properties of wire object type `line`.

All wire objects have a set of basic attributes `{object_id, action, type, persist, data}`. The `data` attribute defines the object-specific attributes

## Line Attributes

| Attribute | Type | Default | Description | Required |
| :--- | :--- | :--- | :--- | :--- |
| **data** | Line data | | Line object data properties as defined below | Yes |
| **color** | string | `'#74BEC1'` | Line color. | Yes |
| **end** | [Vector3](Vector3) |  | Vector3 | Yes |
| **opacity** | number | `1` | Line opacity. | No |
| **start** | [Vector3](Vector3) |  | Vector3 | Yes |
| **visible** | boolean | `True` | Whether object is visible. Property is inherited. | No |
| **parent** | string |  | Parent's object_id. Child objects inherit attributes of their parent, for example scale and translation. | No |
| **position** | [Position](Position) |  | 3D object position. | No |
| **rotation** | [Rotation](Rotation) |  | 3D object rotation in quaternion representation; Right-handed coordinate system. Euler degrees are deprecated in wire message format. | No |
| **scale** | [Scale](Scale) |  | 3D object scale. | No |

