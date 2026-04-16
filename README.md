# arena-schemas
Schemas for objects used in the ARENA.

There are a handful of scripts and run commands that can update schemas and generate intermediate json schema and markdown documents.

## Documentation
- [Requirements & Architecture](REQUIREMENTS.md)
- [Contributing](CONTRIBUTING.md)

## Generate Intermediate Schema (required)
Step 1. This will take a source directory, like the arena-web-core build directory and parse it's `[src]/schemas/` for  `arena-schema-files.json` to output expanded json schema in our local schema dir `./schemas/`, removing older `.json` schema files if needed.
```bash
make update src=~/git/arena-services-docker/arena-web-core/build/schemas
```

## Generate Linked Markdown (required)
Step 2. This will take the expanded json schema in our local schema dir `./schemas/`, and generate formatted tables of schema in Markdown format linked together with descriptions in our local markdown output folder `./docs`, removing older `.md` Markdown files if needed.
```bash
make docs dst=./docs
```

## Generate Jekyll Markdown (optional)
Step 3. This will take a destination directory where jekyll Markdown should be created. It will use `./schemas/arena-schema-files.json` to generate an `index.md` file and copy it and all of the `.md` in `./docs` to `[dst]/`. The process will add the appropriate Jekyll preamble to the beginning of the destination `.md` files.
```bash
make jekyll dst=~/git/arena-docs/content/schemas/message
```

## Generate Python Schema Classes (independent)
This will read directly from your `src` directory of message schema (usually `arena-web-core/build`), and update your local `arena-py` repo at the `dst` location. It will generate missing classes in Python, and update only the first docstring of any existing Python classes.

```bash
make py dst=~/git/arena-py/arena
```

## Generate Unity Schema Classes (independent)
This will read directly from your `src` directory of message schema (usually `arena-web-core/build`), and update your local `arena-unity` repo at the `dst` location. It will overwrite the entire folder and write the JSON serialization classes for the entire schema in .NET C# for Unity.

```bash
make dotnet dst=~/git/arena-unity/Runtime/Schemas
```

## Update Repos Everything All At Once
```bash
make update src=~/git/arena-services-docker/arena-web-core/build/schemas
make docs dst=./docs
make jekyll dst=~/git/arena-docs/content/schemas/message
make py dst=~/git/arena-py/arena
make dotnet dst=~/git/arena-unity/Runtime/Schemas
```
