
Cone
====


Cone Geometry

All wire objects have a set of basic attributes ```{object_id, action, type, persist, data}```. The ```data``` attribute defines the object-specific attributes
Cone Attributes
---------------

|Attribute|Description|Type|Default|Required|
| :--- | :--- | :--- | :--- | :--- |
|object_id|A uuid or otherwise unique identifier for this object|string||Yes|
|action|One of 3 basic Create/Update/Delete actions or a special client event action (e.g. a click)|string; One of: ```['create', 'delete', 'update', 'clientEvent']```|```'create'```|Yes|
|type|AFrame 3D Object|string; Must be: ```object```|```'object'```|Yes|
|persist|Persist this object in the database (default false = do not persist)|boolean|```true```|Yes|
|data|Cone Data|Cone data||Yes|

### Cone Data Attributes

|Attribute|Description|Type|Default|Required|
| :--- | :--- | :--- | :--- | :--- |
|object_type|3D object type.|string; Must be: ```cone```|```cone```|Yes|
|height|height|number|```2```|Yes|
|openEnded|open ended|boolean|```False```|No|
|radiusBottom|radius bottom|number|```1```|Yes|
|radiusTop|radius top|number|```1```|No|
|segmentsRadial|segments radial|number|```36```|No|
|segmentsHeight|segments height|number|```18```|No|
|thetaStart|theta start|number|```0```|No|
|thetaLength|theta length|number|```360```|No|
|buffer|See: [buffer.md](buffer.md)|buffer||No|
|skipCache|See: [skipCache.md](skipCache.md)|skipCache||No|
|position|See: [position.md](position.md)|position|```{'x': 0, 'y': 0, 'z': 0}```|No|
|rotation|See: [rotation.md](rotation.md)|rotation|```{'x': 0, 'y': 0, 'z': 0}```|No|
|scale|See: [scale.md](scale.md)|scale||No|
|material|See: [material.md](material.md)|material|```{'color': '#7f7f7f'}```|No|
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
|text|See: [text.md](text.md)|text||No|
|shadow|See: [shadow.md](shadow.md)|shadow||No|
