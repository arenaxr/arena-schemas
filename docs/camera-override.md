
Camera Override
===============


Camera Override

All wire objects have a set of basic attributes ```{object_id, action, type, persist, data}```. The ```data``` attribute defines the object-specific attributes

Camera Override Attributes
---------------------------

|Attribute|Type|Default|Description|Required|
| :--- | :--- | :--- | :--- | :--- |
|**object_id**|string||Object identifier; Must be a valid camera ID.|Yes|
|**action**|string; One of: ```['create', 'delete', 'update']```|```'update'```|Message action create, update, delete.|Yes|
|**persist**|boolean|```False```|Persist this object in the database.|Yes|
|**type**|string; Must be: ```camera-override```|```'camera-override'```|ARENA camera override data|Yes|
|**data**|[camera-override](camera-override)||Object data payload; Camera Override config data.|Yes|

### Camera Override Data Attributes
