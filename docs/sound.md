
Sound
=====


The sound component defines the entity as a source of sound or audio. The sound component can be positional and is thus affected by the component's position.

More properties at <a href='https://aframe.io/docs/1.5.0/components/sound.html'>A-Frame Sound</a>.

Sound Attributes
-----------------

|Attribute|Type|Default|Description|Required|
| :--- | :--- | :--- | :--- | :--- |
|**autoplay**|boolean|```False```|Whether to automatically play sound once set.|No|
|**distanceModel**|string; One of: ```['linear', 'inverse', 'exponential']```|```'inverse'```|Sound model.|No|
|**loop**|boolean|```False```|Whether to loop the sound once the sound finishes playing.|No|
|**maxDistance**|number|```10000```|Maximum distance between the audio source and the listener, after which the volume is not reduced any further.|No|
|**on**|string; One of: ```['mousedown', 'mouseup', 'mouseenter', 'mouseleave', 'triggerdown', 'triggerup', 'gripdown', 'gripup', 'menudown', 'menuup', 'systemdown', 'systemup', 'trackpaddown', 'trackpadup']```|```'mousedown'```|An event for the entity to listen to before playing sound.|No|
|**poolSize**|number|```1```|Numbers of simultaneous instances of this sound that can be playing at the same time.|No|
|**positional**|boolean|```True```|Whether or not the audio is positional (movable).|No|
|**refDistance**|number|```1```|Reference distance for reducing volume as the audio source moves further from the listener.|No|
|**rolloffFactor**|number|```1```|Describes how quickly the volume is reduced as the source moves away from the listener.|No|
|**src**|string||URL path to sound file e.g. 'store/users/wiselab/sound/wave.mp3'.|No|
|**volume**|number|```1```|How loud to play the sound.|No|
