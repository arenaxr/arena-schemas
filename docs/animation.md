
Animation
=========


Animate and tween values.

More properties at <a href='https://aframe.io/docs/1.5.0/components/animation.html'>A-Frame Animation</a> component. Easing properties are detailed at <a href='https://easings.net'>easings.net</a>.

Animation Attributes
---------------------

|Attribute|Type|Default|Description|Required|
| :--- | :--- | :--- | :--- | :--- |
|**autoplay**|boolean|```True```|Whether or not the animation should autoplay. Should be specified if the animation is defined for the animation-timeline component (currently not supported).|No|
|**delay**|number|```0```|How long (milliseconds) to wait before starting.|No|
|**dir**|string; One of: ```['normal', 'alternate', 'reverse']```|```'normal'```|Which dir to go from from to to.|No|
|**dur**|number|```1000```|How long (milliseconds) each cycle of the animation is.|No|
|**easing**|string; One of: ```['easeInQuad', 'easeInCubic', 'easeInQuart', 'easeInQuint', 'easeInSine', 'easeInExpo', 'easeInCirc', 'easeInBack', 'easeInElastic', 'easeOutQuad', 'easeOutCubic', 'easeOutQuart', 'easeOutQuint', 'easeOutSine', 'easeOutExpo', 'easeOutCirc', 'easeOutBack', 'easeOutElastic', 'easeInOutQuad', 'easeInOutCubic', 'easeInOutQuart', 'easeInOutQuint', 'easeInOutSine', 'easeInOutExpo', 'easeInOutCirc', 'easeInOutBack', 'easeInOutElastic', 'linear']```|```'easeInQuad'```|Easing function of animation. To ease in, ease out, ease in and out. See easings.net for more.|No|
|**elasticity**|number|```400```|How much to bounce (higher is stronger).|No|
|**enabled**|boolean|```True```|If disabled, animation will stop and startEvents will not trigger animation start.|No|
|**from**|string|```''```|Initial value at start of animation. If not specified, the current property value of the entity will be used (will be sampled on each animation start). It is best to specify a from value when possible for stability.|No|
|**isRawProperty**|boolean|```False```|Flag to animate an arbitrary object property outside of A-Frame components for better performance. If set to true, for example, we can set property to like components.material.material.opacity. If property starts with components or object3D, this will be inferred to true.|No|
|**loop**|string|```'0'```|How many times the animation should repeat. If the value is true, the animation will repeat infinitely.|No|
|**pauseEvents**|array|```[]```|Comma-separated list of events to listen to trigger pause. Can be resumed with resumeEvents.|No|
|**property**|string||Property to animate. Can be a component name, a dot-delimited property of a component (e.g., material.color), or a plain attribute.|No|
|**resumeEvents**|array|```[]```|Comma-separated list of events to listen to trigger resume after pausing.|No|
|**round**|boolean|```False```|Whether to round values.|No|
|**startEvents**|array|```[]```|Comma-separated list of events to listen to trigger a restart and play. Animation will not autoplay if specified. startEvents will restart the animation, use pauseEvents to resume it. If there are other animation components on the entity animating the same property, those animations will be automatically paused to not conflict.|No|
|**to**|string|```''```|Target value at end of animation.|No|
|**type**|string|```''```|Right now only supports color for tweening isRawProperty color XYZ/RGB vector values.|No|
