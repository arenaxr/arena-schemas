
Line
====


Draw a line

All wire objects have a set of basic attributes ```{object_id, action, type, persist, data}```. The ```data``` attribute defines the object-specific attributes
Line Attributes
---------------

|Attribute|Description|Type|Default|Required|
| :--- | :--- | :--- | :--- | :--- |
|object_id|A uuid or otherwise unique identifier for this object|string||Yes|
|action|One of 3 basic Create/Update/Delete actions or a special client event action (e.g. a click)|string; One of: ```['create', 'delete', 'update', 'clientEvent']```|```'create'```|Yes|
|type|AFrame 3D Object|string; Must be: ```object```|```'object'```|Yes|
|persist|Persist this object in the database (default false = do not persist)|boolean|```true```|Yes|
|data|Line Data|Line data||Yes|

### Line Data Attributes

|Attribute|Description|Type|Default|Required|
| :--- | :--- | :--- | :--- | :--- |
|object_type|3D object type.|string; Must be: ```line```|```line```|Yes|
|start|See: [coord3d.md](coord3d.md)|coord3d|```{'x': 0, 'y': 0.5, 'z': 0}```|Yes|
|end|See: [coord3d.md](coord3d.md)|coord3d|```{'x': -0.5, 'y': -0.5, 'z': 0}```|Yes|
|opacity|Line Opacity|number|```1```|No|
|visible|Visible|boolean|```True```|No|
|color|See: [color.md](color.md)|color|```white```|No|
|parent|See: [parent.md](parent.md)|parent||No|
|text|See: [text.md](text.md)|text||No|
|shadow|See: [shadow.md](shadow.md)|shadow||No|
