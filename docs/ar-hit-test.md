
AR Hit Test Settings
====================


A-Frame AR Hit Test Settings.

More properties at <a href='https://aframe.io/docs/1.5.0/components/ar-hit-test.html'>AR Hit Test</a> component.

AR Hit Test Settings Attributes
--------------------------------

|Attribute|Type|Default|Description|Required|
| :--- | :--- | :--- | :--- | :--- |
|**enabled**|boolean|```True```|Whether to do hit-testing or not.|Yes|
|**src**|string|```'static/images/reticle-gray.png'```|Image to use for the reticle.|Yes|
|**type**|string; One of: ```['footprint', 'map']```|```'footprint'```|Footprint is the shape of the model.|No|
|**footprintDepth**|number|```0.1```|Amount of the model used for the footprint, 1 is full height.|No|
|**mapSize**|string|```'0.5 0.5'```|If no target is set then this is the size of the map.|No|
