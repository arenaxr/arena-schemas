
Environment Presets
===================


Environment Presets
Environment Presets Attributes
------------------------------

|Attribute|Description|Type|Default|Required|
| :--- | :--- | :--- | :--- | :--- |
|active|Show/hides the environment presets component. Use this instead of using the visible attribute.|boolean|```True```|Yes|
|preset|An A-frame preset environment.|string; One of: ```['none', 'default', 'contact', 'egypt', 'checkerboard', 'forest', 'goaland', 'yavapai', 'goldmine', 'arches', 'threetowers', 'poison', 'tron', 'japan', 'dream', 'volcano', 'starry', 'osiris']```|```'default'```|Yes|
|seed|Seed for randomization. If you don't like the layout of the elements, try another value for the seed.|number|```1```|No|
|skyType|A sky type|string; One of: ```['none', 'color', 'gradient', 'atmosphere']```|```'color'```|No|
|skyColor|Sky Color|string|```'#ffa500'```|No|
|horizonColor|Horizon Color|string|```'#ffa500'```|No|
|lighting|A hemisphere light and a key light (directional or point) are added to the scene automatically when using the component. Use none if you don't want this automatic lighting set being added. The color and intensity are estimated automatically.|string; One of: ```['none', 'distant', 'point']```|```'distant'```|No|
|shadow|Shadows on/off. Sky light casts shadows on the ground of all those objects with shadow component applied|boolean|```False```|No|
|shadowSize|Size of the shadow, if applied|number|```10```|No|
|lightPosition|See: [coord3d.md](coord3d.md)|coord3d|```{'x': 0, 'y': 1, 'z': -0.2}```|No|
|fog|Amount of fog (0 = none, 1 = full fog). The color is estimated automatically.|number|```0```|No|
|flatShading|Whether to show everything smoothed (false) or polygonal (true).|boolean|```False```|No|
|playArea|Radius of the area in the center reserved for the player and the gameplay. The ground is flat in there and no objects are placed inside.|number|```1```|No|
|ground|Orography style.|string; One of: ```['none', 'flat', 'hills', 'canyon', 'spikes', 'noise']```|```'hills'```|No|
|groundScale|See: [coord3d.md](coord3d.md)|coord3d|```{'x': 1, 'y': 1, 'z': 1}```|No|
|groundYScale|Maximum height (in meters) of ground's features (hills, mountains, peaks..).|number|```3```|No|
|groundTexture|Texture applied to the ground.|string; One of: ```['none', 'checkerboard', 'squares', 'walkernoise']```|```'none'```|No|
|groundColor|Main color of the ground.|string|```'#553e35'```|No|
|groundColor2|Secondary color of the ground. Used for textures, ignored if groundTexture is none.|string|```'#694439'```|No|
|dressing|Dressing is the term we use here for the set of additional objects that are put on the ground for decoration.|string; One of: ```['none', 'cubes', 'pyramids', 'cylinders', 'hexagons', 'stones', 'trees', 'mushrooms', 'towers', 'apparatus', 'arches', 'torii']```|```'none'```|No|
|dressingAmount|Number of objects used for dressing|number|```10```|No|
|dressingColor|Base color of dressing objects.|string|```'#795449'```|No|
|dressingScale|Height (in meters) of dressing objects.|number|```5```|No|
|dressingVariance|See: [coord3d.md](coord3d.md)|coord3d|```{'x': 1, 'y': 1, 'z': 1}```|No|
|dressingUniformScale|If false, a different value is used for each coordinate x, y, z in the random variance of size.|boolean|```True```|No|
|dressingOnPlayArea|Amount of dressing on play area.|number|```0```|No|
|grid|1x1 and 2x2 are rectangular grids of 1 and 2 meters side, respectively.|string; One of: ```['none', '1x1', '2x2', 'crosses', 'dots', 'xlines', 'ylines']```|```'none'```|No|
|gridColor|Color of the grid.|string|```'#ccc'```|No|
