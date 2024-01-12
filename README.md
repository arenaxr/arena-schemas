# arena-schemas
Schemas for objects used in the ARENA.

There are a handful of scripts and run commands that can update scripts and generate intermediate json schema and markdown documents:

## Generate Intermediate Schema
Step 1. This will take a source directory, like the arena-web-core build directory and parse it's `[src]/schemas/` for  `arena-schema-files.json` to output expanded json schema in our local schema dir `./schemas/`, removing older `.json` schema files if needed.
```bash
make update src=~/git/arena-services-docker/arena-web-core/build/schemas
```

## Generate Linked Markdown
Step 2. This will take the expanded json schema in our local schema dir `./schemas/`, and generate formatted tables of schema in Markdown format linked together with descriptions in our local markdown output folder `./docs`, removing older `.md` Markdown files if needed.
```bash
make docs
```

## Generate Jekyll Markdown
Step 3. This will take a destination directory where jekyll Markdown should be created. It will use `./schemas/arena-schema-files.json` to generate an `index.md` file and copy it and all of the `.md` in `./docs` to `[dst]/`. The process will add the appropriate Jekyll preamble to the beginning of the destination `.md` files.
```bash
make jekyll dst=~/git/arena-docs/content/schemas/message
```

## Update Repos Hat Trick
```bash
make update src=~/git/arena-services-docker/arena-web-core/build
make docs
make jekyll dst=~/git/arena-docs/content/schemas/message
make dotnet dst=~/git/arena-unity/Runtime/Schemas
make py src=~/git/arena-services-docker/arena-web-core/build dst=~/git/arena-py/docstring/
```
