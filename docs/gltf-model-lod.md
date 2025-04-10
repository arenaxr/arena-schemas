
GLTF Model Level of Detail
==========================


Simple switch between the default gltf-model and a detailed one when a user camera is within specified distance. Requires `object_type: gltf-model`.

GLTF Model Level of Detail Attributes
--------------------------------------

|Attribute|Type|Default|Description|Required|
| :--- | :--- | :--- | :--- | :--- |
|**detailedUrl**|string|```''```|Alternative 'detailed' gltf model to load by URL.|Yes|
|**detailedDistance**|number|```10```|At what distance to switch between the models.|Yes|
|**updateRate**|number|```333```|How often user camera is checked for LOD (default 333ms).|Yes|
|**retainCache**|boolean|```False```|Whether to skip freeing the detailed model from browser cache (default false).|Yes|
