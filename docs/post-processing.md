# `post-processing`

These effects are enabled in desktop and XR views.

This is the schema for Post-Processing Effects, the properties of object `post-processing`.

## Post-Processing Effects Attributes

| Attribute | Type | Default | Description | Required |
| :--- | :--- | :--- | :--- | :--- |
| **bloom** | [Bloom](Bloom) |  | Use bloom post-processing effect. | No |
| **sao** | [Sao](Sao) |  | Use scalable ambient occlusion (SAO) post-processing effect. | No |
| **ssao** | [Ssao](Ssao) |  | Use screen space ambient occlusion (SSAO) post-processing effect. | No |
| **pixel** | [Pixel](Pixel) |  | Use Pixelation post-processing effect. | No |
| **glitch** | [Glitch](Glitch) |  | Use Glitch post-processing effect. | No |
| **fxaa** | [Fxaa](Fxaa) |  | Use FXAA post-processing effect. You may want to place this last in effects list. | No |
| **smaa** | [Smaa](Smaa) |  | Use SMAA post-processing effect. You may want to place this last in effects list. | No |

