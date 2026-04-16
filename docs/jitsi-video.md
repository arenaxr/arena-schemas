# `jitsi-video`

Apply a jitsi video source to the geometry.

This is the schema for Jitsi Video, the properties of object `jitsi-video`.

**Used by:** [Box](box), [Capsule](capsule), [Circle](circle), [Cone](cone), [Cube (deprecated; don't use)](cube), [Cylinder](cylinder), [Dodecahedron](dodecahedron), [Icosahedron](icosahedron), [Image](image), [OBJ Model](obj-model), [Octahedron](octahedron), [Plane](plane), [Ring](ring), [Rounded Box](roundedbox), [Sphere](sphere), [Tetrahedron](tetrahedron), [Torus](torus), [Torus Knot](torusKnot), [Triangle](triangle), [Videosphere](videosphere)

## Jitsi Video Attributes

| Attribute | Type | Default | Description | Required |
| :--- | :--- | :--- | :--- | :--- |
| **jitsiId** | string |  | JitsiId of the video source; If defined will override displayName. | No |
| **displayName** | string |  | ARENA or Jitsi display name of the video source; Will be ignored if jitsiId is given. (* change requires reload* ). | Yes |

