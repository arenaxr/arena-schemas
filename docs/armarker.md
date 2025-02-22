
ARMarker
========


A location marker (such as an AprilTag, a lightAnchor, or an UWB tag), used to anchor scenes, or scene objects, in the real world.

ARMarker Attributes
--------------------

|Attribute|Type|Default|Description|Required|
| :--- | :--- | :--- | :--- | :--- |
|**publish**|boolean|```False```|Publish detections. Send detections to external agents (e.g. external builder script that places new markers in the scene). If dynamic=true and publish=true, object position is not updated (left up to external agent).|No|
|**buildable**|boolean|```False```|Whether tag has 'dynamic' toggled on click. Used to position a tag, then lock into position.|Yes|
|**dynamic**|boolean|```False```|Dynamic tag, not used for localization. E.g., to move object to which this ARMarker component is attached to. Requires permissions to update the scene (if dynamic=true).|Yes|
|**ele**|number|```0```|Tag elevation in meters.|No|
|**lat**|number|```0```|Tag latitude.|No|
|**long**|number|```0```|Tag longitude.|No|
|**markerid**|string|```'0'```|The marker id (e.g. for AprilTag 36h11 family, an integer in the range [0, 586]).|Yes|
|**markertype**|string; One of: ```['apriltag_36h11', 'lightanchor', 'uwb', 'vive', 'optitrack']```|```'apriltag_36h11'```|The marker type, technology-based.|Yes|
|**size**|number|```150```|Tag size in millimeters.|Yes|
|**url**|string|```''```|URL associated with the tag.|No|
