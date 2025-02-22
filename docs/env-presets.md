
Environment Presets
===================


A-Frame Environment presets.

More properties at <a href='https://github.com/supermedium/aframe-environment-component'>A-Frame Environment Component</a>.

Environment Presets Attributes
-------------------------------

|Attribute|Type|Default|Description|Required|
| :--- | :--- | :--- | :--- | :--- |
|**active**|boolean|```True```|Shows or hides the environment presets component. Use this instead of using the visible attribute.|Yes|
|**dressing**|string; One of: ```['apparatus', 'arches', 'cubes', 'cylinders', 'hexagons', 'mushrooms', 'none', 'pyramids', 'stones', 'torii', 'towers', 'trees']```|```'none'```|Dressing is the term we use here for the set of additional objects that are put on the ground for decoration.|No|
|**dressingAmount**|integer|```10```|Number of objects used for dressing.|No|
|**dressingColor**|string|```'#795449'```|Base color of dressing objects.|No|
|**dressingOnPlayArea**|number|```0```|Amount of dressing on play area.|No|
|**dressingScale**|number|```5```|Height (in meters) of dressing objects.|No|
|**dressingUniformScale**|boolean|```True```|If false, a different value is used for each coordinate x, y, z in the random variance of size.|No|
|**dressingVariance**|[vector3](vector3)|```{'x': 1, 'y': 1, 'z': 1}```|Maximum x,y,z meters to randomize the size and rotation of each dressing object. Use 0 0 0 for no variation in size nor rotation.|No|
|**flatShading**|boolean|```False```|Whether to show everything smoothed (false) or polygonal (true).|No|
|**fog**|number|```0```|Amount of fog (0 = none, 1 = full fog). The color is estimated automatically.|No|
|**grid**|string; One of: ```['1x1', '2x2', 'crosses', 'dots', 'none', 'xlines', 'ylines']```|```'none'```|1x1 and 2x2 are rectangular grids of 1 and 2 meters side, respectively.|No|
|**gridColor**|string|```'#ccc'```|Color of the grid.|No|
|**ground**|string; One of: ```['canyon', 'flat', 'hills', 'noise', 'none', 'spikes']```|```'hills'```|Orography style.|No|
|**groundColor**|string|```'#553e35'```|Main color of the ground.|No|
|**groundColor2**|string|```'#694439'```|Secondary color of the ground. Used for textures, ignored if groundTexture is none.|No|
|**groundScale**|[vector3](vector3)|```{'x': 1, 'y': 1, 'z': 1}```|Ground dimensions (in meters).|No|
|**groundTexture**|string; One of: ```['checkerboard', 'none', 'squares', 'walkernoise']```|```'none'```|Texture applied to the ground.|No|
|**groundYScale**|number|```3```|Maximum height (in meters) of ground's features (hills, mountains, peaks..).|No|
|**hideInAR**|boolean|```True```|If true, hide the environment when entering AR.|No|
|**horizonColor**|string|```'#ffa500'```|Horizon Color|No|
|**lighting**|string; One of: ```['distant', 'none', 'point']```|```'distant'```|A hemisphere light and a key light (directional or point) are added to the scene automatically when using the component. Use none if you don't want this automatic lighting set being added. The color and intensity are estimated automatically.|No|
|**lightPosition**|[vector3](vector3)|```{'x': 0, 'y': 1, 'z': -0.2}```|Position of the main light. If skyType is atmospheric, only the orientation matters (is a directional light) and it can turn the scene into night when lowered towards the horizon.|No|
|**playArea**|number|```1```|Radius of the area in the center reserved for the player and the gameplay. The ground is flat in there and no objects are placed inside.|No|
|**preset**|string; One of: ```['arches', 'checkerboard', 'contact', 'default', 'dream', 'egypt', 'forest', 'goaland', 'goldmine', 'japan', 'none', 'osiris', 'poison', 'starry', 'threetowers', 'tron', 'volcano', 'yavapai']```|```'default'```|An A-frame preset environment.|Yes|
|**seed**|integer|```1```|Seed for randomization. If you don't like the layout of the elements, try another value for the seed.|No|
|**shadow**|boolean|```False```|Shadows on/off. Sky light casts shadows on the ground of all those objects with shadow component applied.|No|
|**shadowSize**|number|```10```|Size of the shadow, if applied.|No|
|**skyColor**|string|```'#ffa500'```|Sky Color|No|
|**skyType**|string; One of: ```['atmosphere', 'color', 'gradient', 'none']```|```'color'```|A sky type.|No|
