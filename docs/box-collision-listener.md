
Box Collision Listener
======================


Listen for bounding-box collisions with user camera and hands. Must be applied to an object or model with geometric mesh. Collisions are determined by course bounding-box overlaps.

Box Collision Listener Attributes
----------------------------------

|Attribute|Type|Default|Description|Required|
| :--- | :--- | :--- | :--- | :--- |
|**enabled**|boolean|```True```|Publish detections, set `false` to disable.|No|
|**dynamic**|boolean|```False```|Set true for a moving object, which should have its bounding box recalculated regularly to determine proper collision.|Yes|
