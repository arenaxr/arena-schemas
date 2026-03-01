# `ocean`

Flat-shaded ocean primitive.

This is the schema for Ocean, the properties of wire object type `ocean`.

All wire objects have a set of basic attributes `{object_id, action, type, persist, data}`. The `data` attribute defines the object-specific attributes

## Ocean Attributes

| Attribute | Type | Default | Description | Required |
| :--- | :--- | :--- | :--- | :--- |
| **data** | Ocean data | | Ocean object data properties as defined below | Yes |
| **width** | number | `10` | Width of the ocean area. | Yes |
| **depth** | number | `10` | Depth of the ocean area. | Yes |
| **density** | number | `10` | Density of waves. | No |
| **amplitude** | number | `0.1` | Wave amplitude. | No |
| **amplitudeVariance** | number | `0.3` | Wave amplitude variance. | No |
| **speed** | number | `1` | Wave speed. | No |
| **speedVariance** | number | `2` | Wave speed variance. | No |
| **color** | string | `'#7AD2F7'` | Wave color. | Yes |
| **opacity** | number | `0.8` | Wave opacity. | No |
| **parent** | string |  | Parent's object_id. Child objects inherit attributes of their parent, for example scale and translation. | No |
| **position** | [Position](position) |  | 3D object position. | Yes |
| **rotation** | [Rotation](rotation) |  | 3D object rotation in quaternion representation; Right-handed coordinate system. Euler degrees are deprecated in wire message format. | Yes |
| **scale** | [Scale](scale) |  | 3D object scale. | No |
| **visible** | boolean | `True` | Whether object is visible. Property is inherited. | No |

