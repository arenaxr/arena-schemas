
Light
=====


A light

All wire objects have a set of basic attributes ```{object_id, action, type, persist, data}```. The ```data``` attribute defines the object-specific attributes
Light Attributes
----------------

|Attribute|Description|Type|Default|Required|
| :--- | :--- | :--- | :--- | :--- |
|object_id|A uuid or otherwise unique identifier for this object|string||Yes|
|action|One of 3 basic Create/Update/Delete actions or a special client event action (e.g. a click)|string; One of: ```['create', 'delete', 'update', 'clientEvent']```|```'create'```|Yes|
|type|AFrame 3D Object|string; Must be: ```object```|```'object'```|Yes|
|persist|Persist this object in the database (default false = do not persist)|boolean|```true```|Yes|
|data|Light Data|Light data||Yes|

### Light Data Attributes

|Attribute|Description|Type|Default|Required|
| :--- | :--- | :--- | :--- | :--- |
|object_type|3D object type.|string; Must be: ```light```|```light```|Yes|
|light|These attributes (light, intensity, color, ...) can be set directly on the light object (instead of this light attribute inside the light object); dont use in new light objects|||No|
|type|One of ambient, directional, hemisphere, point, spot.|string; One of: ```['ambient', 'directional', 'hemisphere', 'point', 'spot']```|```directional```|No|
|color|Light color.|string|```#ffffff```|No|
|intensity|Light strength.|number|```1```|No|
|groundColor|Light color from below. NOTE: Hemisphere light type only|string|```'#ffffff'```|No|
|decay|Amount the light dims along the distance of the light. NOTE: Point and Spot light type only.|number|```1.0```|No|
|distance|Distance where intensity becomes 0. If distance is 0, then the point light does not decay with distance. NOTE: Point and Spot light type only.|number|```0.0```|No|
|angle|Maximum extent of spot light from its direction (in degrees). NOTE: Spot light type only.|number|```60```|No|
|penumbra|Percent of the spotlight cone that is attenuated due to penumbra. NOTE: Spot light type only.|number|```0.0```|No|
|target|Id of element the spot should point to. set to null to transform spotlight by orientation, pointing to it’s -Z axis. NOTE: Spot light type only.|string|```'None'```|No|
|castShadow|castShadow (point, spot, directional)|boolean|```False```|No|
|shadowBias|shadowBias (castShadow=true)|number|```0```|No|
|shadowCameraFar|shadowCameraFar (castShadow=true)|number|```500```|No|
|shadowCameraFov|shadowCameraFov (castShadow=true)|number|```90```|No|
|shadowCameraNear|shadowCameraNear (castShadow=true)|number|```0.5```|No|
|shadowCameraTop|shadowCameraTop (castShadow=true)|number|```5```|No|
|shadowCameraRight|shadowCameraRight (castShadow=true)|number|```5```|No|
|shadowCameraBottom|shadowCameraBottom (castShadow=true)|number|```-5```|No|
|shadowCameraLeft|shadowCameraBottom (castShadow=true)|number|```-5```|No|
|shadowCameraVisible|shadowCameraVisible (castShadow=true)|boolean|```False```|No|
|shadowMapHeight|shadowMapHeight (castShadow=true)|number|```512```|No|
|shadowMapWidth|shadowMapWidth (castShadow=true)|number|```512```|No|
|shadowRadius|shadowRadius (castShadow=true)|number|```1```|No|
|position|See: [position.md](position.md)|position|```{'x': 0, 'y': 0, 'z': 0}```|No|
|rotation|See: [rotation.md](rotation.md)|rotation|```{'x': 0, 'y': 0, 'z': 0}```|No|
|scale|See: [scale.md](scale.md)|scale|```{'x': 1, 'y': 1, 'z': 1}```|No|
|parent|See: [parent.md](parent.md)|parent||No|
