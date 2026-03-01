# `physx-joint`

Creates a PhysX joint between an ancestor rigid body and a target rigid body. Position and rotation of the entity will be used to create the corresponding joint. Requires `scene-options: physics`.

This is the schema for PhysX Joint, the properties of object `physx-joint`.

## PhysX Joint Attributes

| Attribute | Type | Default | Description | Required |
| :--- | :--- | :--- | :--- | :--- |
| **type** | string; One of: `['Spherical', 'Fixed', 'Revolute', 'Prismatic', 'D6']` | `'Spherical'` | Rigid body joint type to use. Each type has different movement constraints. | No |
| **target** | string |  | Target object selector. Must be an entity having the physx-body component. If not specified, joins to the initial position in the world. | No |
| **breakForce** | [Vector2](vector2) |  | Vector2 | No |
| **removeElOnBreak** | boolean | `False` | If true, removes the entity containing this component when the joint is broken. | No |
| **collideWithTarget** | boolean | `False` | If false, collision will be disabled between the rigid body containing the joint and the target rigid body. | No |
| **softFixed** | boolean | `False` | When used with a D6 type, sets up a 'soft' fixed joint. E.g., for grabbing things. | No |
| **projectionTolerance** | [Vector2](vector2) |  | Vector2 | No |

