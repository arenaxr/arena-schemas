
Line
====


Draw a line

All wire objects have a set of basic attributes ```{object_id, action, type, persist, data}```. The ```data``` attribute defines the object-specific attributes

Line Attributes
----------------

|Attribute|Description|Type|Default|Required|
| :--- | :--- | :--- | :--- | :--- |
|object_id|A uuid or otherwise unique identifier for this object|string||Yes|
|persist|Persist this object in the database (default true = persist on server)|boolean|```true```|Yes|
|type|AFrame 3D Object|string; Must be: ```object```|```'object'```|Yes|
|action|One of 3 basic Create/Update/Delete actions or a special client event action (e.g. a click)|string; One of: ```['create', 'delete', 'update', 'clientEvent']```|```'create'```|Yes|
|data|Line Data|Line data||Yes|

### Line Data Attributes

|Attribute|Description|Type|Default|Required|
| :--- | :--- | :--- | :--- | :--- |
|object_type|3D object type.|string; Must be: ```line```|```line```|Yes|
|end|vertex B (end)||```{'x': -0.5, 'y': -0.5, 'z': 0}```|Yes|
|opacity|Line Opacity|number|```1```|No|
|start|vertex A (start)||```{'x': 0, 'y': 0.5, 'z': 0}```|Yes|
|visible|Visible|boolean|```True```|No|
|animation|See: [animation.md](animation.md)|animation||No|
|armarker|See: [armarker.md](armarker.md)|armarker||No|
|click-listener|Object will listen for clicks|boolean||No|
|collision-listener|Name of the collision-listener, default can be empty string|string||No|
|color|Color|string|```#7f7f7f```|No|
|dynamic-body|See: [dynamic-body.md](dynamic-body.md)|dynamic-body||No|
|goto-url|See: [goto-url.md](goto-url.md)|goto-url||No|
|hide-on-enter-ar|Hide object when entering AR. Remove component to *not* hide|boolean; Must be: ```True```|```True```|No|
|impulse|See: [impulse.md](impulse.md)|impulse||No|
|landmark|See: [landmark.md](landmark.md)|landmark||No|
|material-extras|See: [material-extras.md](material-extras.md)|material-extras||No|
|parent|Parent's object_id. Child objects inherit attributes of their parent, for example scale and translation.|string||No|
|position|See: [position.md](position.md)|position||No|
|rotation|See: [rotation.md](rotation.md)|rotation||No|
|scale|See: [scale.md](scale.md)|scale||No|
|shadow|See: [shadow.md](shadow.md)|shadow||No|
|sound|See: [sound.md](sound.md)|sound||No|
|url|Model URL. Store files paths under 'store/users/<username>' (e.g. store/users/wiselab/models/factory_robot_arm/scene.gltf); to use CDN, prefix with 'https://arena-cdn.conix.io/' (e.g. https://arena-cdn.conix.io/store/users/wiselab/models/factory_robot_arm/scene.gltf)|string||No|
|screenshareable|Whether or not a user can screenshare on an object|boolean|```True```|No|
|video-control|See: [video-control.md](video-control.md)|video-control||No|
|buffer|Transform geometry into a BufferGeometry to reduce memory usage at the cost of being harder to manipulate (geometries only: box, circle, cone, ...).|boolean|```true```|No|
|jitsi-video|See: [jitsi-video.md](jitsi-video.md)|jitsi-video||No|
|material|See: [material.md](material.md)|material||No|
|multisrc|See: [multisrc.md](multisrc.md)|multisrc||No|
|skipCache|Disable retrieving the shared geometry object from the cache. (geometries only: box, circle, cone, ...).|boolean|```true```|No|
