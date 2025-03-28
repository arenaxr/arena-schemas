
Physics Dynamic Body
====================


A freely-moving object. Dynamic bodies have mass, collide with other objects, bounce or slow during collisions, and fall if gravity is enabled. Requires `scene-options: physics`.

More properties at <a href='https://github.com/c-frame/aframe-physics-system/blob/master/CannonDriver.md'>A-Frame Physics System</a>.

Physics Dynamic Body Attributes
--------------------------------

|Attribute|Type|Default|Description|Required|
| :--- | :--- | :--- | :--- | :--- |
|**mass**|number|```5```|Simulated mass of the object, > 0.|No|
|**linearDamping**|number|```0.01```|Resistance to movement.|No|
|**angularDamping**|number|```0.01```|Resistance to rotation.|No|
|**shape**|string; One of: ```['auto', 'box', 'cylinder', 'sphere', 'hull', 'none']```|```'auto'```|Body components will attempt to find an appropriate CANNON.js shape to fit your model. When defining an object you may choose a shape or leave the default, auto. Select a shape carefully, as there are performance implications with different choices.|No|
|**cylinderAxis**|string; One of: ```['x', 'y', 'z']```|```'y'```|Override default axis of bounding cylinder. Requires `shape: cylinder`.|No|
|**sphereRadius**|number||Override default radius of bounding sphere. Requires `shape: sphere`. NaN by default.|No|
|**type**|string; One of: ```['dynamic', 'static']```|```'dynamic'```|Define the result of collisions. Dynamic can be moved, Static cannot be moved.|No|
