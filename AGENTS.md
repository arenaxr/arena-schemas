# Agent Guide

Orientation for agents (and humans) working in this repo. Detailed docs live in the files below — this file is just the index.

## Start here
- [README.md](README.md) — what arena-schemas is: schema definitions for objects used in the ARENA, with scripts for multi-target code generation (JSON Schema, markdown docs).
- [REQUIREMENTS.md](REQUIREMENTS.md) — machine- and human-readable reference for the schema definitions and code generation pipeline.

## Conventions & development rules
- [CONTRIBUTING.md](CONTRIBUTING.md) — contribution guide for ARENA projects.

## Generated documentation
The [docs/](docs/) directory contains auto-generated markdown documentation from schemas:
- [docs/arena-message.md](docs/arena-message.md) — ARENA message format specification.
- Object schemas: `docs/obj-*.md` — one file per ARENA object type (box, sphere, gltf-model, camera, etc.).
- Attribute schemas: `docs/attr-*.md` — one file per ARENA attribute (animation, material, physics, position, rotation, scale, etc.).
