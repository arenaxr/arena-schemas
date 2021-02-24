
Landmarks
=========


ARENA Scene Landmark List

All wire objects have a set of basic attributes ```{object_id, action, type, persist, data}```. The ```data``` attribute defines the object-specific attributes
Landmarks Attributes
--------------------

|Attribute|Description|Type|Default|Required|
| :--- | :--- | :--- | :--- | :--- |
|object_id|A uuid or otherwise unique identifier for this object|string|```'scene-landmarks'```|Yes|
|action|One of 3 basic Create/Update/Delete actions|string; One of: ```['create', 'delete', 'update']```|```'create'```|Yes|
|persist|Persist this object in the database|boolean|```true```|Yes|
|type|ARENA landmarks|string; Must be: ```landmarks```|```'landmarks'```|Yes|
|data|Landmark List|Landmarks data||Yes|

### Landmarks Data Attributes

|Attribute|Description|Type|Default|Required|
| :--- | :--- | :--- | :--- | :--- |
|landmarks|List of landmarks of the scene|array||Yes|
