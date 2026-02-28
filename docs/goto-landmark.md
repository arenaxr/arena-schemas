# `goto-landmark`

Teleports user to the landmark with the given name. Requires `click-listener` attribute.

This is the schema for Goto Landmark, the properties of object `goto-landmark`.

## Goto Landmark Attributes

| Attribute | Type | Default | Description | Required |
| :--- | :--- | :--- | :--- | :--- |
| **on** | string; One of: `['mousedown', 'mouseup']` | `'mousedown'` | Event to listen 'on'. | Yes |
| **landmark** | string | `''` | Id of landmark to teleport to. | Yes |

