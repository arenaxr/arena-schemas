
GLTF Model Update
=================


The GLTF-specific `modelUpdate` attribute is an object with child component names as keys. The top-level keys are the names of the child components to be updated. The values of each are nested `position` and `rotation` attributes to set as new values, respectively. Either `position` or `rotation` can be omitted if unchanged.

GLTF Model Update Attributes
-----------------------------

|Attribute|Type|Default|Description|Required|
| :--- | :--- | :--- | :--- | :--- |
|^[A-Za-z][A-Za-z0-9_-]*$|object||One of this model's named child components.|No|


GLTF Model Update Example
--------------------------


```json
{
    "left-elbow": {
        "position": {
            "x": 0,
            "y": 0,
            "z": 0
        },
        "rotation": {
            "w": 1,
            "x": 0,
            "y": 0,
            "z": 0
        }
    },
    "right-elbow": {
        "rotation": {
            "w": 1,
            "x": 0,
            "y": 0,
            "z": 0
        }
    },
    "left-knee": {}
}
```