
Shadow
======


The shadow component enables shadows for an entity and its children. Adding the shadow component alone is not enough to display shadows in your scene. We must have at least one light with castShadow: true enabled.

Shadow Attributes
------------------

|Attribute|Type|Default|Description|Required|
| :--- | :--- | :--- | :--- | :--- |
|**cast**|boolean|```False```|Whether the entity casts shadows onto the surrounding scene.|Yes|
|**receive**|boolean|```False```|Whether the entity receives shadows from the surrounding scene.|Yes|
