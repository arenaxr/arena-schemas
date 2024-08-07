
Camera
======


Camera is the pose and arena-user component data representing a user avatar.

All wire objects have a set of basic attributes ```{object_id, action, type, persist, data}```. The ```data``` attribute defines the object-specific attributes

Camera Attributes
------------------

|Attribute|Type|Default|Description|Required|
| :--- | :--- | :--- | :--- | :--- |
|object_id|string||A uuid or otherwise unique identifier for this object.|Yes|
|persist|boolean|```True```|Persist this object in the database.|Yes|
|type|string; Must be: ```object```|```'object'```|AFrame 3D Object|Yes|
|action|string; One of: ```['create', 'delete', 'update']```|```'create'```|Message action create, update, delete.|Yes|
|ttl|integer||When applied to an entity, the entity will remove itself from DOM after the specified number of seconds. Update is allowed, which will reset the timer to start from that moment.|No|
|data|Camera data||Camera Data|Yes|

### Camera Data Attributes

|Attribute|Type|Default|Description|Required|
| :--- | :--- | :--- | :--- | :--- |
|object_type|string; Must be: ```camera```|```camera```|3D object type.|Yes|
|arena-user|[arena-user](arena-user)||Another user's camera in the ARENA. Handles Jitsi and display name updates.|Yes|
|parent|string||Parent's object_id. Child objects inherit attributes of their parent, for example scale and translation.|No|
|position|[position](position)||3D object position.|Yes|
|rotation|[rotation](rotation)||3D object rotation in quaternion representation; Right-handed coordinate system. Euler degrees are deprecated in wire message format.|Yes|
|scale|[scale](scale)||3D object scale.|No|
|visible|boolean|```True```|Whether object is visible. Property is inherited.|No|
