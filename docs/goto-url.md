
Goto URL
========


Load new URL when object is clicked. Requires `click-listener` attribute.

Goto URL Attributes
--------------------

|Attribute|Type|Default|Description|Required|
| :--- | :--- | :--- | :--- | :--- |
|**dest**|string; One of: ```['popup', 'newtab', 'sametab']```|```'sametab'```|Where to open the URL.|Yes|
|**on**|string; One of: ```['mousedown', 'mouseup']```|```'mousedown'```|A case-sensitive string representing the event type to listen for. See <a href='https://developer.mozilla.org/en-US/docs/Web/Events'>Web Events</a>.|Yes|
|**url**|string|```''```|The destination url, e.g. https://example.com.|Yes|
