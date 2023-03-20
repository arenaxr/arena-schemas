
Particle System
===============


Particle system component for A-Frame. 

More properties at <a href='https://github.com/c-frame/aframe-particle-system-component'>https://github.com/c-frame/aframe-particle-system-component</a>

Particle System Attributes
---------------------------

|Attribute|Type|Default|Description|Required|
| :--- | :--- | :--- | :--- | :--- |
|preset|string; One of: ```['default', 'dust', 'snow', 'rain']```|```'default'```|Preset configuration. Possible values are: default, dust, snow, rain.|No|
|maxAge|number|```6```|The particle's maximum age in seconds.|No|
|positionSpread|[Vector3](Vector3)|```{x: 0, y: 0, z: 0}```|Describes this emitter's position variance on a per-particle basis.|No|
|type|number|```1```|The default distribution this emitter should use to control its particle's spawn position and force behaviour. Possible values are 1 (box), 2 (sphere), 3 (disc)|No|
|rotationAxis|string; One of: ```['x', 'y', 'x']```|```'x'```|Describes this emitter's axis of rotation. Possible values are x, y and z.|No|
|rotationAngle|number|```0```|The angle of rotation, given in radians. Dust preset is 3.14.|No|
|rotationAngleSpread|number|```0```|The amount of variance in the angle of rotation per-particle, given in radians.|No|
|accelerationValue|[Vector3](Vector3)|```{x: 0, y: -10, z: 0}```|Describes this emitter's base acceleration.|No|
|accelerationSpread|[Vector3](Vector3)|```{x: 10, y: 0, z: 10}```|Describes this emitter's acceleration variance on a per-particle basis.|No|
|velocityValue|[Vector3](Vector3)|```{x: 0, y: 25, z: 0}```|Describes this emitter's base velocity.|No|
|velocitySpread|[Vector3](Vector3)|```{x: 10, y: 7.5, z: 10}```|Describes this emitter's acceleration variance on a per-particle basis.|No|
|dragValue|number|```0```|Number between 0 and 1 describing drag applied to all particles.|No|
|dragSpread|number|```0```|Number describing drag variance on a per-particle basis.|No|
|dragRandomise|boolean|```False```|WHen a particle is re-spawned, whether it's drag should be re-randomised or not. Can incur a performance hit.|No|
|color|array|```['#0000FF', '#FF0000']```|Describes a particle's color. This property is a 'value-over-lifetime' property, meaning an array of values can be given to describe specific value changes over a particle's lifetime.|No|
|size|array|```[1]```|Describes a particle's size.|Yes|
|sizeSpread|array|```[0]```|sizeSpread|No|
|direction|number|```1```|The direction of the emitter. If value is 1, emitter will start at beginning of particle's lifecycle. If value is -1, emitter will start at end of particle's lifecycle and work it's way backwards.|No|
|duration|number|```None```|The duration in seconds that this emitter should live for. If not specified, the emitter will emit particles indefinitely.|No|
|enabled|boolean|```True```|When true the emitter will emit particles, when false it will not. This value can be changed dynamically during a scene. While particles are emitting, they will disappear immediately when set to false.|No|
|particleCount|number|```1000```|The total number of particles this emitter will hold. NOTE: this is not the number of particles emitted in a second, or anything like that. The number of particles emitted per-second is calculated by particleCount |No|
|texture|string|```'static/images/textures/star2.png'```|The texture used by this emitter. Examples: [star2.png, smokeparticle.png, raindrop.png], like path 'static/images/textures/star2.png'|Yes|
|randomise|boolean|```False```|When a particle is re-spawned, whether it's position should be re-randomised or not. Can incur a performance hit.|No|
|opacity|array|```[1]```|Either a single number to describe the opacity of a particle.|No|
|opacitySpread|array|```[1]```|opacitySpread|No|
|blending|string; One of: ```['0', '1', '2', '3', '4']```|```'2'```|The blending mode of the particles. Possible values are 0 (no blending), 1 (normal), 2 (additive), 3 (subtractive), 4 (multiply)|No|
|maxParticleCount|number|```250000```|maxParticleCount|No|