# `event`

Generate an event message for an object.

This is the schema for Event, the properties of wire object type `event`.

All wire objects have a set of basic attributes `{object_id, action, type, persist, data}`. The `data` attribute defines the object-specific attributes

## Event Attributes

| Attribute | Type | Default | Description | Required |
| :--- | :--- | :--- | :--- | :--- |
| **data** | Event data | | Event object data properties as defined below | Yes |
| **target** | string |  | The `object_id` of event destination. | Yes |
| **targetPosition** | [Vector3](Vector3) |  | Vector3 | Yes |
| **originPosition** | [Vector3](Vector3) |  | Vector3 | No |
| **source** | ~~string~~ | ~~~~ | ~~DEPRECATED: data.source is deprecated for clientEvent, use data.target instead.~~ | ~~No~~ |
| **position** | ~~object~~ | ~~~~ | ~~DEPRECATED: data.position is deprecated for clientEvent, use data.targetPosition instead.~~ | ~~No~~ |
| **clickPos** | ~~object~~ | ~~~~ | ~~DEPRECATED: data.clickPos is deprecated for clientEvent, use data.originPosition instead.~~ | ~~No~~ |

