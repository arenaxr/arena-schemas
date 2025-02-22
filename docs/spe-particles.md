
SPE Particles
=============


GPU based particle systems in A-Frame.

More properties at <a href='https://github.com/harlyq/aframe-spe-particles-component'>A-Frame SPE Particles</a> component.

SPE Particles Attributes
-------------------------

|Attribute|Type|Default|Description|Required|
| :--- | :--- | :--- | :--- | :--- |
|**acceleration**|[vector3](vector3)|```{'x': 0, 'y': 0, 'z': 0}```|For sphere and disc distributions, only the x axis is used.|No|
|**accelerationDistribution**|string; One of: ```['none', 'box', 'sphere', 'disc']```|```'none'```|Distribution of particle acceleration, for disc and sphere, only the x component will be used. if set to NONE use the 'distribution' attribute for accelerationDistribution.|No|
|**accelerationSpread**|[vector3](vector3)|```{'x': 0, 'y': 0, 'z': 0}```|Spread of the particle's acceleration. for sphere and disc distributions, only the x axis is used.|No|
|**activeMultiplier**|number|```1```|Multiply the rate of particles emission, if larger than 1 then the particles will be emitted in bursts. note, very large numbers will emit all particles at once.|No|
|**affectedByFog**|boolean|```True```|If true, the particles are affected by THREE js fog.|No|
|**alphaTest**|number|```0```|Alpha values below the alphaTest threshold are considered invisible.|No|
|**angle**|array|```[0]```|2D rotation of the particle over the particle's lifetime, max 4 elements.|No|
|**angleSpread**|array|```[0]```|Spread in angle over the particle's lifetime, max 4 elements.|No|
|**blending**|string; One of: ```['no', 'normal', 'additive', 'subtractive', 'multiply', 'custom']```|```'normal'```|Blending mode, when drawing particles.|No|
|**color**|array|```['#fff']```|Array of colors over the particle's lifetime, max 4 elements.|No|
|**colorSpread**|array|```[]```|Spread to apply to colors, spread an array of vec3 (r g b) with 0 for no spread. note the spread will be re-applied through-out the lifetime of the particle.|No|
|**depthTest**|boolean|```True```|If true, don't render a particle's pixels if something is closer in the depth buffer.|No|
|**depthWrite**|boolean|```False```|If true, particles write their depth into the depth buffer. this should be false if we use transparent particles.|No|
|**direction**|string; One of: ```['forward', 'backward']```|```'forward'```|Make the emitter operate forward or backward in time.|No|
|**distribution**|string; One of: ```['box', 'sphere', 'disc']```|```'box'```|Distribution for particle positions, velocities and acceleration. will be overridden by specific '...Distribution' attributes.|No|
|**drag**|number|```0```|Apply resistance to moving the particle, 0 is no resistance, 1 is full resistance, particle will stop moving at half of it's maxAge.|No|
|**dragSpread**|number|```0```|Spread to apply to the drag attribute.|No|
|**duration**|number|```-1```|Duration of the emitter (seconds), if less than 0 then continuously emit particles.|No|
|**emitterScale**|number|```100```|Global scaling factor for all particles from the emitter.|No|
|**enableInEditor**|boolean|```False```|Enable the emitter while the editor is active (i.e. while scene is paused).|No|
|**enabled**|boolean|```True```|Enable/disable the emitter.|No|
|**frustumCulled**|boolean|```False```|Enable/disable frustum culling.|No|
|**hasPerspective**|boolean|```True```|If true, particles will be larger the closer they are to the camera.|No|
|**maxAge**|number|```1```|Maximum age of a particle before reusing.|No|
|**maxAgeSpread**|number|```0```|Variance for the 'maxAge' attribute.|No|
|**opacity**|array|```[1]```|Opacity over the particle's lifetime, max 4 elements.|No|
|**opacitySpread**|array|```[0]```|Spread in opacity over the particle's lifetime, max 4 elements.|No|
|**particleCount**|integer|```100```|Maximum number of particles for this emitter.|No|
|**positionDistribution**|string; One of: ```['none', 'box', 'sphere', 'disc']```|```'none'```|Distribution of particle positions, disc and sphere will use the radius attributes. For box particles emit at 0,0,0, for sphere they emit on the surface of the sphere and for disc on the edge of a 2D disc on the XY plane.|No|
|**positionOffset**|[vector3](vector3)|```{'x': 0, 'y': 0, 'z': 0}```|Fixed offset to the apply to the emitter relative to its parent entity.|No|
|**positionSpread**|[vector3](vector3)|```{'x': 0, 'y': 0, 'z': 0}```|Particles are positioned within +- of these local bounds. for sphere and disc distributions only the x axis is used.|No|
|**radius**|number|```1```|Radius of the disc or sphere emitter (ignored for box). note radius of 0 will prevent velocity and acceleration if they use a sphere or disc distribution.|No|
|**radiusScale**|[vector3](vector3)|```{'x': 1, 'y': 1, 'z': 1}```|Scales the emitter for sphere and disc shapes to form oblongs and ellipses.|No|
|**randomizeAcceleration**|boolean|```False```|If true, re-randomize acceleration when re-spawning a particle, can incur a performance hit.|No|
|**randomizeAngle**|boolean|```False```|If true, re-randomize angle when re-spawning a particle, can incur a performance hit.|No|
|**randomizeColor**|boolean|```False```|If true, re-randomize colour when re-spawning a particle, can incur a performance hit.|No|
|**randomizeDrag**|boolean|```False```|If true, re-randomize drag when re-spawning a particle, can incur a performance hit.|No|
|**randomizeOpacity**|boolean|```False```|If true, re-randomize opacity when re-spawning a particle, can incur a performance hit.|No|
|**randomizePosition**|boolean|```False```|If true, re-randomize position when re-spawning a particle, can incur a performance hit.|No|
|**randomizeRotation**|boolean|```False```|If true, re-randomize rotation when re-spawning a particle, can incur a performance hit.|No|
|**randomizeSize**|boolean|```False```|If true, re-randomize size when re-spawning a particle, can incur a performance hit.|No|
|**randomizeVelocity**|boolean|```False```|If true, re-randomize velocity when re-spawning a particle, can incur a performance hit.|No|
|**relative**|string; One of: ```['local', 'world']```|```'local'```|World relative particles move relative to the world, while local particles move relative to the emitter (i.e. if the emitter moves, all particles move with it).|No|
|**rotation**|number|```0```|Rotation in degrees.|No|
|**rotationAxis**|[vector3](vector3)|```{'x': 0, 'y': 0, 'z': 0}```|Local axis when using rotation.|No|
|**rotationAxisSpread**|[vector3](vector3)|```{'x': 0, 'y': 0, 'z': 0}```|Variance in the axis of rotation.|No|
|**rotationSpread**|number|```0```|Rotation variance in degrees.|No|
|**rotationStatic**|boolean|```False```|If true, the particles are fixed at their initial rotation value. if false, the particle will rotate from 0 to the 'rotation' value.|No|
|**size**|array|```[1]```|Array of sizes over the particle's lifetime, max 4 elements.|No|
|**sizeSpread**|array|```[0]```|Spread in size over the particle's lifetime, max 4 elements.|No|
|**texture**|string|```''```|Texture to be used for each particle, may be a spritesheet.  Examples: [blob.png, fog.png, square.png, explosion_sheet.png, fireworks_sheet.png], like path 'static/images/textures/blob.png'.|No|
|**textureFrameCount**|integer|```-1```|Number of frames in the spritesheet, negative numbers default to textureFrames.x * textureFrames.y.|No|
|**textureFrameLoop**|integer|```1```|Number of times the spritesheet should be looped over the lifetime of a particle.|No|
|**textureFrames**|[vector2](vector2)|```{'x': 1, 'y': 1}```|X and Y frames for a spritesheet. each particle will transition through every frame of the spritesheet over its lifetime (see textureFramesLoop).|No|
|**useTransparency**|boolean|```True```|Should the particles be rendered with transparency?|No|
|**velocity**|[vector3](vector3)|```{'x': 0, 'y': 0, 'z': 0}```|For sphere and disc distributions, only the x axis is used.|No|
|**velocityDistribution**|string; One of: ```['none', 'box', 'sphere', 'disc']```|```'none'```|Distribution of particle velocities, for disc and sphere, only the x component will be used. if set to NONE use the 'distribution' attribute for velocityDistribution.|No|
|**velocitySpread**|[vector3](vector3)|```{'x': 0, 'y': 0, 'z': 0}```|Variance for the velocity.|No|
|**wiggle**|number|```0```|Extra distance the particle moves over its lifetime.|No|
|**wiggleSpread**|number|```0```|+- spread for the wiggle attribute.|No|
