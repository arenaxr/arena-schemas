
Text
====


Display text. 

More properties at https://aframe.io/docs/1.3.0/components/text.html

All wire objects have a set of basic attributes ```{object_id, action, type, persist, data}```. The ```data``` attribute defines the object-specific attributes

Text Attributes
----------------

|Attribute|Description|Type|Default|Required|
| :--- | :--- | :--- | :--- | :--- |
|object_id|A uuid or otherwise unique identifier for this object|string||Yes|
|persist|Persist this object in the database (default true = persist on server)|boolean|```true```|Yes|
|type|AFrame 3D Object|string; Must be: ```object```|```'object'```|Yes|
|action|One of 3 basic Create/Update/Delete actions or a special client event action (e.g. a click)|string; One of: ```['create', 'delete', 'update', 'clientEvent']```|```'create'```|Yes|
|data|Text Data|Text data||Yes|

### Text Data Attributes

|Attribute|Description|Type|Default|Required|
| :--- | :--- | :--- | :--- | :--- |
|object_type|3D object type.|string; Must be: ```text```|```text```|Yes|
|alphaTest|alphaTest||```0.5```|No|
|anchor|anchor|; One of: ```['left', 'right', 'center', 'align']```|```center```|No|
|baseline|baseline|; One of: ```['top', 'center', 'bottom']```|```center```|No|
|font|font|string; One of: ```['aileronsemibold', 'dejavu', 'exo2bold', 'exo2semibold', 'kelsonsans', 'monoid', 'mozillavr', 'roboto', 'sourcecodepro']```|```roboto```|No|
|fontImage|fontImage|string||No|
|height|height|number||No|
|letterSpacing|letterSpacing|number|```0```|No|
|lineHeight|lineHeight|number||No|
|negate|negate|boolean|```True```|No|
|opacity|opacity|number|```1```|No|
|shader|shader|; One of: ```['portal', 'flat', 'standard', 'sdf', 'msdf', 'ios10hls', 'skyshader', 'gradientshader']```|```sdf```|No|
|side|side|; One of: ```['front', 'back', 'double']```|```double```|No|
|tabSize|tabSize||```4```|No|
|text|Please use attribute 'value' in new Text objects;|string||No|
|transparent|transparent||```True```|No|
|value|Any string of ASCII characters. e.g. 'Hello world!'|string|``````|No|
|whiteSpace|whiteSpace|; One of: ```['normal', 'pre', 'nowrap']```|```normal```|No|
|width|width|number|```5```|No|
|wrapCount|wrapCount|number|```40```|No|
|wrapPixels|wrapPixels|number||No|
|xOffset|xOffset|number|```0```|No|
|yOffset|yOffset|number|```0```|No|
|zOffset|zOffset|number|```0.001```|No|
|animation|See: [animation.md](animation.md)|animation||No|
|armarker|See: [armarker.md](armarker.md)|armarker||No|
|click-listener|Object will listen for clicks|boolean||No|
|collision-listener|Name of the collision-listener, default can be empty string|string||No|
|color|Color|string|```white```|No|
|dynamic-body|See: [dynamic-body.md](dynamic-body.md)|dynamic-body||No|
|goto-url|See: [goto-url.md](goto-url.md)|goto-url||No|
|hide-on-enter-ar|Hide object when entering AR. Remove component to *not* hide|boolean; Must be: ```True```|```True```|No|
|impulse|See: [impulse.md](impulse.md)|impulse||No|
|landmark|See: [landmark.md](landmark.md)|landmark||No|
|material-extras|See: [material-extras.md](material-extras.md)|material-extras||No|
|parent|Parent's object_id. Child objects inherit attributes of their parent, for example scale and translation.|string||No|
|position|See: [position.md](position.md)|position|```{'x': 0, 'y': 0, 'z': 0}```|No|
|rotation|See: [rotation.md](rotation.md)|rotation|```{'x': 0, 'y': 0, 'z': 0}```|No|
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
