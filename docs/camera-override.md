# `camera-override`

Object data payload; Camera Override config data.

This is the schema for Camera Override Data, the properties of object `camera-override`.

## Camera Override Data Attributes

| Attribute | Type | Default | Description | Required |
| :--- | :--- | :--- | :--- | :--- |
| **target** | string |  | Look at target object_id or position. Requires `object_type: look-at`. | No |
| **landmarkObj** | string |  | Teleport to the same id as the target object. Requires `object_type: teleport-to-landmark`. | No |
| **parent** | string |  | Parent's object_id. Child objects inherit attributes of their parent, for example scale and translation. | No |
| **position** | [Position](Position) |  | 3D object position. | No |
| **rotation** | [Rotation](Rotation) |  | 3D object rotation in quaternion representation; Right-handed coordinate system. Euler degrees are deprecated in wire message format. | No |
| **scale** | [Scale](Scale) |  | 3D object scale. | No |
| **visible** | boolean | `True` | Whether object is visible. Property is inherited. | No |

