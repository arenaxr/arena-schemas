
User Avatar
===========


Another user's camera in the ARENA. Handles Jitsi and display name updates.

User Avatar Attributes
-----------------------

|Attribute|Type|Default|Description|Required|
| :--- | :--- | :--- | :--- | :--- |
|**displayName**|string|```''```|User display name.|Yes|
|**color**|string|```'white'```|The color for the user's name text.|Yes|
|**headModelPath**|string|```'/static/models/avatars/robobit.glb'```|Path to user avatar head model.|Yes|
|**presence**|string; One of: ```['Standard', 'Portal']```|```'Standard'```|Type of presence for user.|No|
|**jitsiId**|string|```''```|User Jitsi ID.|No|
|**hasAudio**|bool|```False```|Whether the user has audio on.|No|
|**hasVideo**|bool|```False```|Whether the user has video on.|No|
|**hasAvatar**|bool|```False```|Whether the user has facial feature capture on.|No|
