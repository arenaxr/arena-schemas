
Blip Effect
===========


When the object is created or deleted, it will animate in/out of the scene instead of appearing/disappearing instantly. Must have a geometric mesh.

Blip Effect Attributes
-----------------------

|Attribute|Type|Default|Description|Required|
| :--- | :--- | :--- | :--- | :--- |
|**blipin**|boolean|```True```|Animate in on create, set false to disable.|Yes|
|**blipout**|boolean|```True```|Animate out on delete, set false to disable.|Yes|
|**geometry**|string; One of: ```['rect', 'disk', 'ring']```|```'rect'```|Geometry of the blipout plane.|Yes|
|**planes**|string; One of: ```['both', 'top', 'bottom']```|```'both'```|Which which clipping planes to use for effect. A top plane clips above it, bottom clips below it.|Yes|
|**duration**|number|```750```|Animation duration in milliseconds.|Yes|
|**applyDescendants**|boolean|```False```|Apply blipout effect to include all descendents. Does not work for blipin.|No|
