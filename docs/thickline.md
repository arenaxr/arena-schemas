
Thickline
=========


Draw a line that can have a custom width

All wire objects have a set of basic attributes ```{object_id, action, type, persist, data}```. The ```data``` attribute defines the object-specific attributes
Thickline Attributes
--------------------

|Attribute|Description|Type|Default|Required|
| :--- | :--- | :--- | :--- | :--- |
|object_id|A uuid or otherwise unique identifier for this object|string||Yes|
|action|One of 3 basic Create/Update/Delete actions or a special client event action (e.g. a click)|string; One of: ```['create', 'delete', 'update', 'clientEvent']```|```'create'```|Yes|
|type|AFrame 3D Object|string; Must be: ```object```|```'object'```|Yes|
|persist|Persist this object in the database (default false = do not persist)|boolean|```true```|Yes|
|data|Thickline Data|Thickline data||Yes|

### Thickline Data Attributes

|Attribute|Description|Type|Default|Required|
| :--- | :--- | :--- | :--- | :--- |
|object_type|3D object type.|string; Must be: ```thickline```|```thickline```|Yes|
|path|Line Path|string|```-2 -1 0, 0 20 0, 10 -1 10```|Yes|
|lineWidth|Line width|number|```5```|No|
|lineWidthStyle|Line width Style|number|```1```|No|
|color|See: [color.md](color.md)|color|```#7f7f7f```|No|
|parent|See: [parent.md](parent.md)|parent||No|
|text|See: [text.md](text.md)|text||No|
|shadow|See: [shadow.md](shadow.md)|shadow||No|
