
Renderer Settings
=================


Renderer Settings
Renderer Settings Attributes
----------------------------

|Attribute|Description|Type|Default|Required|
| :--- | :--- | :--- | :--- | :--- |
|gammaFactor|Gamma factor (three.js default is 2.0; we use 2.2 as default)|number|```2.2```|No|
|localClippingEnabled|Defines whether the renderer respects object-level clipping planes|boolean|```False```|No|
|outputEncoding|Defines the output encoding of the renderer (three.js default is LinearEncoding; we use sRGBEncoding as default)|string; One of: ```['LinearEncoding', 'sRGBEncoding', 'GammaEncoding', 'RGBEEncoding', 'LogLuvEncoding', 'RGBM7Encoding', 'RGBM16Encoding', 'RGBDEncoding', 'BasicDepthPacking', 'RGBADepthPacking']```|```'sRGBEncoding'```|Yes|
|physicallyCorrectLights|Whether to use physically correct lighting mode.|boolean|```False```|No|
|sortObjects|Defines whether the renderer should sort objects|boolean|```True```|No|
