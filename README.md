# arena-schemas
Schemas for objects used in the ARENA.

There are a handful of scripts and run commands that can update scripts and generate intermediate json schema and markdown documents:

## Generate Intermediate Schema
Step 1. This will take a source directory, like the ARENA-core build directory and parse it's `[src]/schema/` for  `arena-schema-files.json` to output expanded json schema in our local schema dir `./schema/`, removing older `.json` schema files if needed.
```bash
make update src=~/git/arena-services-docker/ARENA-core/build
```

## Generate Linked Markdown
Step 2. This will take the expanded json schema in our local schema dir `./schema/`, and generate formatted tables of schema in Markdown format linked together with descriptions in our markdown output folder `./docs`, removing older `.md` Markdown files if needed.
```bash
make docs
```
