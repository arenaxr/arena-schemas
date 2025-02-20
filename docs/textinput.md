
Text Input
==========


Opens an HTML prompt when clicked. Sends text input as an event on MQTT. Requires `click-listener` attribute.

Text Input Attributes
----------------------

|Attribute|Type|Default|Description|Required|
| :--- | :--- | :--- | :--- | :--- |
|**on**|string; One of: ```['mousedown', 'mouseup', 'mouseenter', 'mouseleave', 'triggerdown', 'triggerup', 'gripdown', 'gripup', 'menudown', 'menuup', 'systemdown', 'systemup', 'trackpaddown', 'trackpadup']```|```'mousedown'```|A case-sensitive string representing the event type to listen for. See <a href='https://developer.mozilla.org/en-US/docs/Web/Events'>Web Events</a>|Yes|
|**title**|string|```'Text Input'```|The prompt title.|Yes|
|**label**|string|```'Input text below (max is 140 characters).'```|Text prompt label|Yes|
|**placeholder**|string|```'Type here'```|Text input place holder.|Yes|
