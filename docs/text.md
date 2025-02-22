
Text
====


Display text.

More properties at <a href='https://aframe.io/docs/1.5.0/components/text.html'>A-Frame Text</a>.

All wire objects have a set of basic attributes ```{object_id, action, type, persist, data}```. The ```data``` attribute defines the object-specific attributes

Text Attributes
----------------

|Attribute|Type|Default|Description|Required|
| :--- | :--- | :--- | :--- | :--- |
|**object_id**|string||A uuid or otherwise unique identifier for this object.|Yes|
|**persist**|boolean|```True```|Persist this object in the database.|Yes|
|**type**|string; Must be: ```object```|```'object'```|AFrame 3D Object|Yes|
|**action**|string; One of: ```['create', 'delete', 'update']```|```'create'```|Message action create, update, delete.|Yes|
|**ttl**|number||When applied to an entity, the entity will remove itself from DOM after the specified number of seconds. Update is allowed, which will reset the timer to start from that moment.|No|
|**private**|boolean|```False```|If true, interactions with this object should not be broadcasted to other clients, but rather sent on private topics|No|
|**program_id**|string||The program_id on private program topics that interactions to be directed to, if the private flag is set true. Ignored if private flag is false.|No|
|**data**|Text data||Text Data|Yes|

### Text Data Attributes

|Attribute|Type|Default|Description|Required|
| :--- | :--- | :--- | :--- | :--- |
|**object_type**|string; Must be: ```text```|```text```|3D object type.|Yes|
|**align**|string; One of: ```['left', 'center', 'right']```|```'left'```|Multi-line text alignment.|No|
|**alphaTest**|number|```0.5```|Discard text pixels if alpha is less than this value.|No|
|**anchor**|string; One of: ```['left', 'right', 'center', 'align']```|```'center'```|Horizontal positioning.|No|
|**baseline**|string; One of: ```['top', 'center', 'bottom']```|```'center'```|Vertical positioning.|No|
|**color**|string|```'#000000'```|Text color.|Yes|
|**font**|string; One of: ```['aileronsemibold', 'dejavu', 'exo2bold', 'exo2semibold', 'kelsonsans', 'monoid', 'mozillavr', 'roboto', 'sourcecodepro']```|```'roboto'```|Font to render text, either the name of one of A-Frame's stock fonts or a URL to a font file.|Yes|
|**fontImage**|string||Font image texture path to render text. Defaults to the font's name with extension replaced to .png. Don't need to specify if using a stock font. (derived from font name).|No|
|**height**|number||Height of text block. (derived from text size).|No|
|**letterSpacing**|number|```0```|Letter spacing in pixels.|No|
|**lineHeight**|number||Line height in pixels. (derived from font file).|No|
|**opacity**|number|```1```|Opacity, on a scale from 0 to 1, where 0 means fully transparent and 1 means fully opaque.|No|
|**shader**|string; One of: ```['portal', 'flat', 'standard', 'sdf', 'msdf', 'ios10hls', 'skyshader', 'gradientshader']```|```'sdf'```|Shader used to render text.|No|
|**side**|string; One of: ```['front', 'back', 'double']```|```'double'```|Side to render.|Yes|
|**tabSize**|number|```4```|Tab size in spaces.|No|
|~~**text**~~|~~string~~||~~DEPRECATED: data.text is deprecated for object_type: text, use data.value instead.~~|~~No~~|
|**transparent**|boolean|```True```|Whether text is transparent.|No|
|**value**|string||The actual content of the text. Line breaks and tabs are supported with `\n` and `\t`.|Yes|
|**whiteSpace**|string; One of: ```['normal', 'pre', 'nowrap']```|```'normal'```|How whitespace should be handled.|No|
|**width**|number|```5```|Width in meters. (derived from geometry if exists).|No|
|**wrapCount**|number|```40```|Number of characters before wrapping text (more or less).|No|
|**wrapPixels**|number||Number of pixels before wrapping text. (derived from wrapCount).|No|
|**xOffset**|number|```0```|X-offset to apply to add padding.|No|
|**zOffset**|number|```0.001```|Z-offset to apply to avoid Z-fighting if using with a geometry as a background.|No|
|**parent**|string||Parent's object_id. Child objects inherit attributes of their parent, for example scale and translation.|No|
|**position**|[position](position)||3D object position.|Yes|
|**rotation**|[rotation](rotation)||3D object rotation in quaternion representation; Right-handed coordinate system. Euler degrees are deprecated in wire message format.|Yes|
|**scale**|[scale](scale)||3D object scale.|No|
|**visible**|boolean|```True```|Whether object is visible. Property is inherited.|No|
