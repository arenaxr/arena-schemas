
Scene Options
=============


Scene Options
Scene Options Attributes
------------------------

|Attribute|Description|Type|Default|Required|
| :--- | :--- | :--- | :--- | :--- |
|jitsiServer|Jitsi host used for this scene.|string|```'mr.andrew.cmu.edu'```|No|
|screenshare|Name of the 3D object used when sharing desktop|string|```'screenshare'```|No|
|clickableOnlyEvents|true = publish only mouse events for objects with click-listeners; false = all objects publish mouse events|boolean|```true```|Yes|
|privateScene|false = scene will be visible; true = scene will not show in listings|boolean|```false```|Yes|
|userTeleportDistance|Distance to put user when teleporting to be in front of another user|number|```2```|No|
|landmarkTeleportDistance|Distance to put user when teleporting to be in front of a landmark|number|```3.5```|No|
|volume|Volume for users in a scene|number|```1```|No|
|distanceModel|Algorithm to use to reduce the volume of the audio source as it moves away from the listener|string; One of: ```['inverse', 'linear', 'exponential']```|```'inverse'```|No|
|refDistance|Distance at which the volume reduction starts taking effect|number|```1```|No|
|rolloffFactor|How quickly the volume is reduced as the source moves away from the listener|number|```1```|No|
|maxAVDist|Maximum distance between cameras/users until audio and video are cut off. For saving bandwidth on scenes with large amounts of user activity at once|number|```20```|Yes|
