# `channels`



This is the schema for Channels, the properties of object `channels`.

**Used by:** [Program](program)

## Channels Attributes

| Attribute | Type | Default | Description | Required |
| :--- | :--- | :--- | :--- | :--- |
| **path** | string |  | Folder visible by the program. | No |
| **type** | string; One of: `['pubsub', 'client']` | `'pubsub'` | Pubsub or client socket. | No |
| **mode** | string; One of: `['r', 'w', 'rw']` |  | Access mode. | No |
| **params** | [Params](params) |  | Type (i.e. pubsub/client)-specific parameters. | No |

