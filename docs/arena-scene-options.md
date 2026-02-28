# `arena-scene-options`



This is the schema for Scene Config, the properties of wire object type `arena-scene-options`.

All wire objects have a set of basic attributes `{object_id, action, type, persist, data}`. The `data` attribute defines the object-specific attributes

## Scene Config Attributes

| Attribute | Type | Default | Description | Required |
| :--- | :--- | :--- | :--- | :--- |
| **data** | Scene Config data | | Scene Config object data properties as defined below | Yes |
| **env-presets** | [EnvPresets](EnvPresets) |  | A-Frame Environment presets.

More properties at <a href='https://github.com/supermedium/aframe-environment-component'>A-Frame Environment Component</a>. | Yes |
| **renderer-settings** | [RendererSettings](RendererSettings) |  | These settings are fed into three.js WebGLRenderer properties. | No |
| **scene-options** | [SceneOptions](SceneOptions) |  | ARENA Scene Options. | Yes |
| **post-processing** | [PostProcessing](PostProcessing) |  | These effects are enabled in desktop and XR views. | No |

