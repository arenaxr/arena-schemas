
Material extras
===============


Define extra material properties.
Material extras Attributes
--------------------------

|Attribute|Description|Type|Default|Required|
| :--- | :--- | :--- | :--- | :--- |
|encoding|encoding|string; One of: ```['LinearEncoding', 'sRGBEncoding', 'GammaEncoding', 'RGBEEncoding', 'LogLuvEncoding', 'RGBM7Encoding', 'RGBM16Encoding', 'RGBDEncoding', 'BasicDepthPacking', 'RGBADepthPacking']```|```sRGBEncoding```|No|
|needsUpdate|needsUpdate|boolean|```False```|No|
|render-order|This value allows the default rendering order of scene graph objects to be overridden.|number|```1```|No|
|colorWrite|Whether to render the material’s color|boolean||No|
|transparentOccluder|If true, will set colorWrite=false and renderOrder=0 to make the material a transparent occluder.|boolean||No|
|defaultRenderOrder|Used as the renderOrder when transparentOccluder is reset to false.|number||No|
