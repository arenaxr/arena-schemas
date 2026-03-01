# `physx-joint-constraint`

Adds a constraint to a physx-joint. Supported joints are D6, Revolute and Prismatic. Can only be used on an entity with the physx-joint component. Requires `scene-options: physics`.

This is the schema for PhysX Joint Constraint, the properties of object `physx-joint-constraint`.

## PhysX Joint Constraint Attributes

| Attribute | Type | Default | Description | Required |
| :--- | :--- | :--- | :--- | :--- |
| **lockedAxes** | string[] | `[]` | [D6] Which axes are explicitly locked by this constraint and can't be moved at all. Should be some combination of x, y, z, twist, swing. | No |
| **constrainedAxes** | string[] | `[]` | [D6] Which axes are constrained by this constraint. These axes can be moved within the set limits. Should be some combination of x, y, z, twist, swing. | No |
| **freeAxes** | string[] | `[]` | [D6] Which axes are explicitly freed by this constraint. These axes will not obey any limits set here. Should be some combination of x, y, z, twist, swing. | No |
| **linearLimit** | [Vector2](vector2) |  | Vector2 | No |
| **angularLimit** | [Vector2](vector2) |  | Vector2 | No |
| **limitCone** | [Vector2](vector2) |  | Vector2 | No |
| **twistLimit** | [Vector2](vector2) |  | Vector2 | No |
| **damping** | number | `0` | [All] Spring damping for soft constraints. | No |
| **restitution** | number | `0` | [All] Spring restitution for soft constraints. | No |
| **stiffness** | number | `0` | [All] If greater than 0, will make this joint a soft constraint, and use a spring force model. | No |

