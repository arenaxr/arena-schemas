
SPE Particles
=============


GPU based particle systems in A-Frame. 

More properties at <a href='https://github.com/harlyq/aframe-spe-particles-component'>https://github.com/harlyq/aframe-spe-particles-component</a>

SPE Particles Attributes
-------------------------

|Attribute|Type|Default|Description|Required|
| :--- | :--- | :--- | :--- | :--- |
|acceleration|[Vector3](Vector3)|```{x: 0, y: 0, z: 0}```|for sphere and disc distributions, only the x axis is used|No|
|accelerationDistribution|string; One of: ```['none', 'box', 'sphere', 'disc']```|```'none'```|distribution of particle acceleration, for disc and sphere, only the x component will be used. if set to NONE use the 'distribution' attribute for accelerationDistribution|No|
|accelerationSpread|[Vector3](Vector3)|```{x: 0, y: 0, z: 0}```|spread of the particle's acceleration. for sphere and disc distributions, only the x axis is used|No|
|activeMultiplier|number|```1```|multiply the rate of particles emission, if larger than 1 then the particles will be emitted in bursts. note, very large numbers will emit all particles at once|No|
|affectedByFog|boolean|```True```|if true, the particles are affected by THREE js fog|No|
|alphaTest|number|```0```|alpha values below the alphaTest threshold are considered invisible|No|
|angle|array|```[0]```|2D rotation of the particle over the particle's lifetime, max 4 elements|No|
|angleSpread|array|```[0]```|spread in angle over the particle's lifetime, max 4 elements|No|
|blending|string; One of: ```['no', 'normal', 'additive', 'subtractive', 'multiply', 'custom']```|```'normal'```|blending mode, when drawing particles|No|
|color|array|```['#fff']```|array of colors over the particle's lifetime, max 4 elements|No|
|colorSpread|array|```[]```|spread to apply to colors, spread an array of vec3 (r g b) with 0 for no spread. note the spread will be re-applied through-out the lifetime of the particle|No|
|depthTest|boolean|```True```|if true, don't render a particle's pixels if something is closer in the depth buffer|No|
|depthWrite|boolean|```False```|if true, particles write their depth into the depth buffer. this should be false if we use transparent particles|No|
|direction|string; One of: ```['forward', 'backward']```|```'forward'```|make the emitter operate forward or backward in time|No|
|distribution|string; One of: ```['box', 'sphere', 'disc']```|```'box'```|distribution for particle positions, velocities and acceleration. will be overriden by specific '...Distribution' attributes|No|
|drag|number|```0```|apply resistance to moving the particle, 0 is no resistance, 1 is full resistance, particle will stop moving at half of it's maxAge|No|
|dragSpread|number|```0```|spread to apply to the drag attribute|No|
|duration|number|```-1```|duration of the emitter (seconds), if less than 0 then continuously emit particles|No|
|emitterScale|number|```100```|global scaling factor for all particles from the emitter|No|
|enableInEditor|boolean|```False```|enable the emitter while the editor is active (i.e. while scene is paused)|No|
|enabled|boolean|```True```|enable/disable the emitter|No|
|frustumCulled|boolean|```False```|enable/disable frustum culling|No|
|hasPerspective|boolean|```True```|if true, particles will be larger the closer they are to the camera|No|
|maxAge|number|```1```|maximum age of a particle before reusing|No|
|maxAgeSpread|number|```0```|variance for the 'maxAge' attribute|No|
|opacity|array|```[1]```|opacity over the particle's lifetime, max 4 elements|No|
|opacitySpread|array|```[0]```|spread in opacity over the particle's lifetime, max 4 elements|No|
|particleCount|integer|```100```|maximum number of particles for this emitter|No|
|positionDistribution|string; One of: ```['none', 'box', 'sphere', 'disc']```|```'none'```|distribution of particle positions, disc and sphere will use the radius attributes. For box particles emit at 0,0,0, for sphere they emit on the surface of the sphere and for disc on the edge of a 2D disc on the XY plane|No|
|positionOffset|[Vector3](Vector3)|```{x: 0, y: 0, z: 0}```|fixed offset to the apply to the emitter relative to its parent entity|No|
|positionSpread|[Vector3](Vector3)|```{x: 0, y: 0, z: 0}```|particles are positioned within +- of these local bounds. for sphere and disc distributions only the x axis is used|No|
|radius|number|```1```|radius of the disc or sphere emitter (ignored for box). note radius of 0 will prevent velocity and acceleration if they use a sphere or disc distribution|No|
|radiusScale|[Vector3](Vector3)|```{x: 1, y: 1, z: 1}```|scales the emitter for sphere and disc shapes to form oblongs and ellipses|No|
|randomizeAcceleration|boolean|```False```|if true, re-randomize acceleration when re-spawning a particle, can incur a performance hit|No|
|randomizeAngle|boolean|```False```|if true, re-randomize angle when re-spawning a particle, can incur a performance hit|No|
|randomizeColor|boolean|```False```|if true, re-randomize colour when re-spawning a particle, can incur a performance hit|No|
|randomizeDrag|boolean|```False```|if true, re-randomize drag when re-spawning a particle, can incur a performance hit|No|
|randomizeOpacity|boolean|```False```|if true, re-randomize opacity when re-spawning a particle, can incur a performance hit|No|
|randomizePosition|boolean|```False```|if true, re-randomize position when re-spawning a particle, can incur a performance hit|No|
|randomizeRotation|boolean|```False```|if true, re-randomize rotation when re-spawning a particle, can incur a performance hit|No|
|randomizeSize|boolean|```False```|if true, re-randomize size when re-spawning a particle, can incur a performance hit|No|
|randomizeVelocity|boolean|```False```|if true, re-randomize velocity when re-spawning a particle, can incur a performance hit|No|
|relative|string; One of: ```['local', 'world']```|```'local'```|world relative particles move relative to the world, while local particles move relative to the emitter (i.e. if the emitter moves, all particles move with it)|No|
|rotation|number|```0```|rotation in degrees|No|
|rotationAxis|[Vector3](Vector3)|```{x: 0, y: 0, z: 0}```|local axis when using rotation|No|
|rotationAxisSpread|[Vector3](Vector3)|```{x: 0, y: 0, z: 0}```|variance in the axis of rotation|No|
|rotationSpread|number|```0```|rotation variance in degrees|No|
|rotationStatic|boolean|```False```|if true, the particles are fixed at their initial rotation value. if false, the particle will rotate from 0 to the 'rotation' value|No|
|size|array|```[1]```|array of sizes over the particle's lifetime, max 4 elements|No|
|sizeSpread|array|```[0]```|spread in size over the particle's lifetime, max 4 elements|No|
|texture|string|```''```|texture to be used for each particle, may be a spritesheet.  Examples: [blob.png, fog.png, square.png, explosion_sheet.png, fireworks_sheet.png], like path 'static/images/textures/blob.png'|No|
|textureFrameCount|integer|```-1```|number of frames in the spritesheet, negative numbers default to textureFrames.x * textureFrames.y|No|
|textureFrameLoop|integer|```1```|number of times the spritesheet should be looped over the lifetime of a particle|No|
|textureFrames|[Vector2](Vector2)|```{x: 1, y: 1}```|x and y frames for a spritesheet. each particle will transition through every frame of the spritesheet over its lifetime (see textureFramesLoop)|No|
|useTransparency|boolean|```True```|should the particles be rendered with transparency?|No|
|velocity|[Vector3](Vector3)|```{x: 0, y: 0, z: 0}```|for sphere and disc distributions, only the x axis is used|No|
|velocityDistribution|string; One of: ```['none', 'box', 'sphere', 'disc']```|```'none'```|distribution of particle velocities, for disc and sphere, only the x component will be used. if set to NONE use the 'distribution' attribute for velocityDistribution|No|
|velocitySpread|[Vector3](Vector3)|```{x: 0, y: 0, z: 0}```|variance for the velocity|No|
|wiggle|number|```0```|extra distance the particle moves over its lifetime|No|
|wiggleSpread|number|```0```|+- spread for the wiggle attribute|No|