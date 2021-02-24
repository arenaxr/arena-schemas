
Text
====


Display text

All wire objects have a set of basic attributes ```{object_id, action, type, persist, data}```. The ```data``` attribute defines the object-specific attributes
Text Attributes
---------------

|Attribute|Description|Type|Default|Required|
| :--- | :--- | :--- | :--- | :--- |
|object_id|A uuid or otherwise unique identifier for this object|string||Yes|
|action|One of 3 basic Create/Update/Delete actions or a special client event action (e.g. a click)|string; One of: ```['create', 'delete', 'update', 'clientEvent']```|```'create'```|Yes|
|type|AFrame 3D Object|string; Must be: ```object```|```'object'```|Yes|
|persist|Persist this object in the database (default false = do not persist)|boolean|```true```|Yes|
|data|Text|Text data||Yes|

### Text Data Attributes

|Attribute|Description|Type|Default|Required|
| :--- | :--- | :--- | :--- | :--- |
|object_type|3D object type.|string; Must be: ```text```|```text```|Yes|
|value|Any string of ASCII characters. e.g. 'Hello world!'|string|``````|No|
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
|transparent|transparent||```True```|No|
|whiteSpace|whiteSpace|; One of: ```['normal', 'pre', 'nowrap']```|```normal```|No|
|width|width|number|```5```|No|
|wrapCount|wrapCount|number|```40```|No|
|wrapPixels|wrapPixels|number||No|
|xOffset|xOffset|number|```0```|No|
|yOffset|yOffset|number|```0```|No|
|zOffset|zOffset|number|```0.001```|No|
|text|Please use attribute 'value' in new Text objects;|string||No|
|position|See: [position.md](position.md)|position|```{'x': 0, 'y': 0, 'z': 0}```|No|
|rotation|See: [rotation.md](rotation.md)|rotation|```{'x': 0, 'y': 0, 'z': 0}```|No|
|scale|See: [scale.md](scale.md)|scale||No|
|material|See: [material.md](material.md)|material||No|
|material-extras|See: [material-extras.md](material-extras.md)|material-extras||No|
|multisrc|See: [multisrc.md](multisrc.md)|multisrc||No|
|animation|See: [animation.md](animation.md)|animation||No|
|animation-mixer|See: [animation-mixer.md](animation-mixer.md)|animation-mixer||No|
|sound|See: [sound.md](sound.md)|sound||No|
|dynamic-body|See: [dynamic-body.md](dynamic-body.md)|dynamic-body||No|
|impulse|See: [impulse.md](impulse.md)|impulse||No|
|click-listener|See: [click-listener.md](click-listener.md)|click-listener||No|
|collision-listener|See: [collision-listener.md](collision-listener.md)|collision-listener||No|
|goto-url|See: [goto-url.md](goto-url.md)|goto-url||No|
|video-control|See: [video-control.md](video-control.md)|video-control||No|
|parent|See: [parent.md](parent.md)|parent||No|
|color|See: [color.md](color.md)|color|```white```|No|
|shadow|See: [shadow.md](shadow.md)|shadow||No|
