#!/usr/bin/env python3
import argparse
import json
import os
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import jinja2
from caseconverter import pascalcase, snakecase

# ---------------------------------------------------------------------------
# Core Schema Data Models
# ---------------------------------------------------------------------------

@dataclass
class SchemaProperty:
    """Represents a property inside an ARENA Object."""
    name: str                 # JSON key (e.g. 'color', 'position')
    type_name: str            # 'string', 'number', 'array', or reference name
    description: str = ""
    default: Any = None
    required: bool = False
    is_array: bool = False
    array_item_type: str = ""
    is_ref: bool = False      # Is it strictly a referenced object?
    ref_name: str = ""        # e.g., Vector3
    deprecated: bool = False
    enum: List[str] = field(default_factory=list)

@dataclass
class SchemaObject:
    """Represents a top-level ARENA Object or Component (e.g., Box, Light, Position)."""
    name: str                 # e.g., 'box', 'position'
    title: str = ""           # 'Box Data'
    description: str = ""
    properties: Dict[str, SchemaProperty] = field(default_factory=dict)
    is_component: bool = False # e.g. position, rotation vs box, light


# ---------------------------------------------------------------------------
# Schema Loader & Resolver
# ---------------------------------------------------------------------------

class SchemaLoader:
    """Loads JSON files, resolves $ref and allOf naturally into dictionaries,
    and converts them to our strict SchemaObject/SchemaProperty dataclasses."""

    def __init__(self, src_folder: str):
        self.src_folder = src_folder
        self._raw_cache = {}    # Cache of raw JSON schemas loaded from disk
        self.expanded_cache = {} # The finalized expanded dictionary for saving intermediate
        self.arena_objects: Dict[str, SchemaObject] = {}
        self.components: Dict[str, SchemaObject] = {}

    def get_raw(self, filename: str) -> dict:
        if filename not in self._raw_cache:
            path = os.path.join(self.src_folder, filename)
            if not os.path.exists(path):
                print(f"Warning: {filename} missing from {self.src_folder}")
                return {}
            with open(path, 'r', encoding='utf-8') as f:
                self._raw_cache[filename] = json.load(f)
        return self._raw_cache[filename]

    def _resolve_refs(self, node: Any, base_file: str, definitions: dict) -> Any:
        """Deeply resolves JSON $ref and allOf inside dictionaries."""
        if isinstance(node, list):
            return [self._resolve_refs(item, base_file, definitions) for item in node]

        elif isinstance(node, dict):
            # Resolve allOf
            if "allOf" in node:
                new_dict = {}
                for part in node["allOf"]:
                    resolved_part = self._resolve_refs(part, base_file, definitions)
                    if isinstance(resolved_part, dict):
                        for k, v in resolved_part.items():
                            if k not in new_dict: new_dict[k] = {}
                            if isinstance(v, dict) and isinstance(new_dict[k], dict):
                                new_dict[k].update(v)
                            else:
                                new_dict[k] = v
                # Combine remaining original fields
                for k, v in node.items():
                    if k != "allOf":
                        new_dict[k] = self._resolve_refs(v, base_file, definitions)
                return new_dict

            # Resolve $ref
            if "$ref" in node:
                ref = node["$ref"]
                parts = ref.split("#")

                # External file ref
                if parts[0] != "":
                    ext_file = parts[0]
                    ext_schema = self.get_raw(ext_file)
                    # If it has a path like /definitions/something
                    if len(parts) > 1 and parts[1]:
                        path = parts[1].strip("/").split("/")
                        # Legacy compatibility: in original schemas, refs to #properties
                        # actually intend to merge the entire schema block (properties+required)
                        if path == ["properties"]:
                            return self._resolve_refs(ext_schema, ext_file, ext_schema.get("definitions", {}))

                        curr = ext_schema
                        for p in path: curr = curr.get(p, {})
                        return self._resolve_refs(curr, ext_file, ext_schema.get("definitions", {}))
                    else:
                        return self._resolve_refs(ext_schema, ext_file, ext_schema.get("definitions", {}))

                # Internal map ref against local definitions
                else:
                    path = parts[1].strip("/").split("/") # typically ['definitions', 'xyz']
                    if path[0] == "definitions" and path[1] in definitions:
                        # Copy the dict so we don't accidentally mutate definitions
                        resolved = dict(definitions[path[1]])
                        return self._resolve_refs(resolved, base_file, definitions)

            # standard traversal
            return {k: self._resolve_refs(v, base_file, definitions) for k, v in node.items()}

        else:
            return node

    def build_models(self):
        """Builds expanded JSONs and creates SchemaObjects."""
        list_fns = ["schemas/arena-schema-files.json", "schemas/arena-schema-files-nonpersist.json"]

        obj_schemas = {}
        for list_fn in list_fns:
            fn_dict = self.get_raw(list_fn)
            obj_schemas.update(fn_dict)

        # Parse Arena Objects
        for _, obj_info in obj_schemas.items():
            fn = obj_info["file"]
            raw_schema = self.get_raw(fn)
            definitions = raw_schema.get("definitions", {})

            # 1. Expand raw JSON naturally for the intermediate generation step
            expanded = self._resolve_refs(raw_schema, fn, definitions)
            self.expanded_cache[fn] = expanded

            # 2. Extract Data Objects into dataclasses
            # ARENA messages typically look like: { "properties": { "data": { ... } } }
            data_props = expanded.get("properties", {}).get("data", {})
            if "properties" not in data_props:
                continue

            # Usually the root `filename` object type determines the object properties
            base_name = os.path.splitext(os.path.basename(fn))[0]
            obj_types = data_props.get("properties", {}).get("object_type", {}).get("enum", [])

            # Most things will have an enum array e.g. ["box"], we create an object for each
            for ot in (obj_types if obj_types else [base_name]):
                obj = self._create_schema_object(ot, data_props)
                obj.is_component = False
                obj.title = expanded.get("title", f"{ot.title()} Data")
                obj.description = expanded.get("description", "")
                self.arena_objects[ot] = obj

            # Now we discover the "components" from the inner properties
            # Things like position, rotation, color, etc. that are objects themselves
            for prop_name, prop_data in data_props.get("properties", {}).items():
                if prop_name == "object_type": continue

                # If the inner property is itself an object, we need a component class for it
                if prop_data.get("type") == "object" or prop_data.get("$ref") or "properties" in prop_data:
                    if prop_name not in self.components:
                        comp = self._create_schema_object(prop_name, prop_data)
                        comp.is_component = True
                        comp.title = prop_data.get("title", prop_name.title())
                        comp.description = prop_data.get("description", "")
                        self.components[prop_name] = comp

    def _create_schema_object(self, name: str, schema_dict: dict) -> SchemaObject:
        """Hydrates a SchemaObject dataclass from a processed schema dictionary."""
        obj = SchemaObject(name=name)
        required = schema_dict.get("required", [])
        props = schema_dict.get("properties", {})

        for p_name, p_data in props.items():
            if p_name == "object_type": continue # Skip the wire discriminator

            p_obj = SchemaProperty(name=p_name, type_name="object", required=(p_name in required))
            p_obj.description = p_data.get("description", p_data.get("title", p_name))
            p_obj.default = p_data.get("default")
            p_obj.deprecated = p_data.get("deprecated", False)
            p_obj.enum = p_data.get("enum", [])

            # Type resolution
            t = p_data.get("type", "object")
            p_obj.type_name = t

            if t == "array":
                p_obj.is_array = True
                items = p_data.get("items", {})
                p_obj.array_item_type = items.get("type", "object")

            # Has a ref?
            if p_data.get("$ref") or (t == "object" and "properties" in p_data):
                p_obj.is_ref = True
                p_obj.ref_name = pascalcase(p_data.get("$ref", f"#/{p_name}").split("/")[-1])
                p_obj.type_name = p_obj.ref_name # e.g. 'Vector3'

            obj.properties[p_name] = p_obj

        return obj

# ---------------------------------------------------------------------------
# Generators
# ---------------------------------------------------------------------------

class MarkdownGenerator:
    """Generates pure markdown tables from the loaded SchemaObjects."""

    ObjTypeDesc = {
        "object": "AFrame 3D Object",
        "program": "ARENA program data",
        "scene-options": "ARENA scene options",
        "landmarks": "ARENA landmarks",
        "camera-override": "ARENA camera override data",
    }

    @classmethod
    def format_value(cls, prop: SchemaProperty) -> str:
        if prop.type_name == "string":
            return f"`'{prop.default}'`"
        return f"`{prop.default}`"

    @classmethod
    def generate_table(cls, obj: SchemaObject) -> str:
        lines = ["| Attribute | Type | Default | Description | Required |", "| :--- | :--- | :--- | :--- | :--- |"]

        # Format the main data block first if it's not a component
        if not obj.is_component:
            desc = f"{obj.title} object data properties as defined below"
            lines.append(f"| **data** | {obj.title} data | | {desc} | Yes |")

        for p_name, p in obj.properties.items():
            req = "Yes" if p.required else "No"
            type_str = p.type_name
            desc_str = p.description or p_name
            dft_str = cls.format_value(p) if p.default is not None else ""

            if p.is_ref:
                type_str = f"[{p.ref_name}]({p.ref_name})"

            if p.is_array:
                if p.is_ref:
                    type_str = f"[{p.ref_name}]({p.ref_name})[]"
                else:
                    type_str = f"{p.array_item_type}[]"

            if p.enum:
                if len(p.enum) == 1:
                    type_val = p.enum[0]
                    desc_str = cls.ObjTypeDesc.get(type_val, desc_str)
                    type_str = f"{type_str}; Must be: `{type_val}`"
                    dft_str = f"`{type_val}`" if type_val else dft_str
                else:
                    type_str = f"{type_str}; One of: `{p.enum}`"

            if p.deprecated:
                req = f"~~{req}~~"
                type_str = f"~~{type_str}~~"
                dft_str = f"~~{dft_str}~~"
                desc_str = f"~~{desc_str}~~"

            lines.append(f"| **{p_name}** | {type_str} | {dft_str} | {desc_str} | {req} |")

        return "\n".join(lines)

    @classmethod
    def generate_all(cls, loader: SchemaLoader, out_folder: str = "docs"):
        """Entrypoint for `python build_schemas3.py docs`"""
        print(f"Generating standard markdown docs to {out_folder}/")
        os.makedirs(out_folder, exist_ok=True)

        # Wipe old
        import glob
        for f in glob.glob(f"{out_folder}/*.md"): os.remove(f)

        def write_md(obj: SchemaObject, wire_obj: bool):
            md = [f"# `{obj.name}`\n"]

            schema_desc = f"This is the schema for {obj.title}, the properties of {'wire object type' if wire_obj else 'object'} `{obj.name}`."
            md.append(f"{obj.description}\n\n{schema_desc}\n")

            if wire_obj:
                md.append("All wire objects have a set of basic attributes `{object_id, action, type, persist, data}`. The `data` attribute defines the object-specific attributes\n")

            md.append(f"## {obj.title} Attributes\n")
            md.append(cls.generate_table(obj))
            md.append("\n")

            p_path = os.path.join(out_folder, f"{obj.name}.md")
            print(f"-> {p_path}")
            with open(p_path, "w", encoding='utf-8') as f:
                f.write("\n".join(md))

        for _, obj in loader.arena_objects.items(): write_md(obj, wire_obj=True)
        for _, obj in loader.components.items(): write_md(obj, wire_obj=False)


class JekyllGenerator:
    """Combines Markdown generator output into the formatted Jekyll site files."""

    @classmethod
    def generate_all(cls, loader: SchemaLoader, out_folder: str):
        print(f"Generating Jekyll site to {out_folder}/")
        os.makedirs(out_folder, exist_ok=True)

        import glob
        for f in glob.glob(f"{out_folder}/*.md"): os.remove(f)

        sec_title = "ARENA Objects"
        sec_sub_title = "Objects Schema"

        # 1. Index Page
        index_md = [
            "---",
            f"title: {sec_sub_title}",
            "layout: default",
            f"parent: {sec_title}",
            "has_children: true",
            "has_toc: false",
            "---",
            "\n<!--CAUTION: This file is autogenerated from https://github.com/arenaxr/arena-schemas. Changes made here may be overwritten.-->\n",
            "# ARENA Message Objects\n",
            "|Object Message|Description|",
            "| :--- | :--- |"
        ]

        for name, obj in sorted(loader.arena_objects.items()):
            index_md.append(f"|[{obj.title}]({name})|{obj.description.splitlines()[0] if obj.description else ''}|")

        index_path = os.path.join(out_folder, "index.md")
        with open(index_path, "w", encoding="utf-8") as f:
            f.write("\n".join(index_md) + "\n")

        # 2. Sub Pages (We'll regenerate them from the schema directly instead of reading the filesystem)
        for _, obj in loader.arena_objects.items():
            cls._write_jekyll_page(obj, sec_title, sec_sub_title, out_folder, wire_obj=True)
        for _, obj in loader.components.items():
            cls._write_jekyll_page(obj, sec_title, sec_sub_title, out_folder, wire_obj=False)

    @classmethod
    def _write_jekyll_page(cls, obj: SchemaObject, sec_title: str, sec_sub_title: str, out_folder: str, wire_obj: bool):
        page_md = [
            "---",
            f"title: {obj.name}",
            "layout: default",
            f"parent: {sec_sub_title}",
            f"grand_parent: {sec_title}",
            "---",
            "\n<!--CAUTION: This file is autogenerated from https://github.com/arenaxr/arena-schemas. Changes made here may be overwritten.-->\n",
            f"# `{obj.name}`\n"
        ]

        schema_desc = f"This is the schema for {obj.title}, the properties of {'wire object type' if wire_obj else 'object'} `{obj.name}`."
        page_md.append(f"{obj.description}\n\n{schema_desc}\n")

        if wire_obj:
            page_md.append("All wire objects have a set of basic attributes `{object_id, action, type, persist, data}`. The `data` attribute defines the object-specific attributes\n")

        page_md.append(f"## {obj.title} Attributes\n")
        page_md.append(MarkdownGenerator.generate_table(obj))
        page_md.append("\n")

        out_path = os.path.join(out_folder, f"{obj.name}.md")
        print(f"-> {out_path}")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write("\n".join(page_md))

class PythonGenerator:
    """Safely updates python class docstrings using regex/AST mapping."""

    @classmethod
    def generate_all(cls, loader: SchemaLoader, out_folder: str):
        print(f"Updating Python docstrings in {out_folder}/")

        # Determine the target classes from the schemas
        for name, obj in loader.arena_objects.items():
            cls._update_py_class(obj, os.path.join(out_folder, "objects"), is_component=False)
        for name, obj in loader.components.items():
            cls._update_py_class(obj, os.path.join(out_folder, "attributes"), is_component=True)

    @classmethod
    def _get_py_type(cls, prop: SchemaProperty) -> str:
        t = prop.type_name
        if t == "number": return "float"
        if t == "integer": return "int"
        if t == "boolean": return "bool"
        if t == "string": return "str"
        if t == "array": return "list"
        if t == "object": return "dict"
        return t # Ref types like Vector3

    @classmethod
    def _generate_docstring(cls, obj: SchemaObject, is_component: bool) -> str:
        lines = [f"\"\"\"\n{obj.title}"]
        if obj.description:
            lines.append(f"{obj.description}")
        lines.append("")

        # Build Args
        for p_name, p in obj.properties.items():
            py_type = cls._get_py_type(p)
            req = "" if p.required else ", optional"

            dft_str = ""
            if p.default is not None:
                dft_str = f" Defaults to {p.default}"
                if p.type_name == 'string':
                    dft_str = f" Defaults to '{p.default}'"

            opts_str = ""
            if p.enum:
                 if len(p.enum) == 1:
                     opts_str = f" Must be '{p.enum[0]}'."
                 else:
                     opts_str = f" Allows {p.enum}."

            desc = p.description or p_name
            lines.append(f":param {py_type} {p_name}: {desc}{req}.{opts_str}{dft_str}")

        lines.append('"""')
        return "\n".join(lines)

    @classmethod
    def _update_py_class(cls, obj: SchemaObject, folder: str, is_component: bool):
        # We need to map schema name to python filename. python uses snake_case and removes `_data` or `_options` sometimes
        # To be completely safe and match existing, we search the folder for a class matching the pascal case name.
        class_name = pascalcase(obj.name)
        if class_name == "SceneOptions": class_name = "Scene"
        if class_name == "MaterialExtension": class_name = "MaterialExt"

        import glob
        py_files = glob.glob(os.path.join(folder, "*.py"))

        target_file = None
        file_content = ""

        # Search all files for `class ClassName(` or `class ClassName:`
        class_def_re = re.compile(r"^class\s+" + class_name + r"[\(:]", re.MULTILINE)

        for pf in py_files:
            with open(pf, "r", encoding="utf-8") as f:
                content = f.read()
            if class_def_re.search(content):
                target_file = pf
                file_content = content
                break

        if not target_file:
            print(f"Skipping Python for {class_name}, file not found in {folder}")
            return

        # We found the file. Now carefully replace the docstring immediately following the class def.
        match = class_def_re.search(file_content)
        start_idx = match.end()

        # Find the very next """ or ''' block
        doc_start = file_content.find('"""', start_idx)
        alt_doc_start = file_content.find("'''", start_idx)

        if doc_start == -1 and alt_doc_start == -1:
            print(f"Warning: No existing docstring found in {target_file} for {class_name}")
            return

        quote_type = '"""' if doc_start != -1 and (alt_doc_start == -1 or doc_start < alt_doc_start) else "'''"
        actual_start = file_content.find(quote_type, start_idx)
        actual_end = file_content.find(quote_type, actual_start + 3) + 3

        if actual_end < 3: # Not found correctly
             return

        # Extract indentation
        line_start = file_content.rfind("\n", 0, actual_start)
        indent = file_content[line_start+1:actual_start]
        if not indent.isspace(): indent = "    "

        new_doc = cls._generate_docstring(obj, is_component)
        # Indent everything
        indented_doc = "\n".join([(indent + line if line else line) for line in new_doc.split("\n")])
        indented_doc = indented_doc.lstrip() # first line already has indent from the original string replacement

        new_content = file_content[:actual_start] + indented_doc + file_content[actual_end:]
        with open(target_file, "w", encoding="utf-8") as f:
            f.write(new_content)
        print(f"-> Updated {os.path.basename(target_file)} ({class_name})")

class DotnetGenerator:
    """Generates clean Unity C# classes using Jinja2 templates."""

    @classmethod
    def get_cs_type(cls, prop: SchemaProperty) -> str:
        t = prop.type_name
        is_array = prop.is_array

        # Base translation check
        if prop.is_ref:
            cs = f"Arena{prop.ref_name}Json"
        elif t == "number":
            cs = "float"
        elif t == "integer":
            cs = "int"
        elif t == "boolean":
            cs = "bool"
        elif t == "string":
            cs = "string"
        elif t == "array":
            # For array, we only map basic inner types. Not heavily needed if ref
            item_t = prop.array_item_type
            inner_cs = "object"
            if item_t == "number": inner_cs = "float"
            elif item_t == "integer": inner_cs = "int"
            elif item_t == "string": inner_cs = "string"
            elif item_t == "boolean": inner_cs = "bool"
            cs = inner_cs
        else:
            cs = "object"

        if is_array:
            return f"{cs}[]"
        return cs

    @classmethod
    def format_default(cls, prop: SchemaProperty, cs_type: str) -> str:
        d = prop.default
        if d is None: return ""
        if isinstance(d, bool): return str(d).lower()
        if cs_type == "float" or cs_type == "float[]":
            if isinstance(d, list): return f"[{', '.join(f'{x}f' for x in d)}]"
            return f"{d}f"
        if cs_type == "string": return f"\"{d}\""
        return str(d)

    @classmethod
    def generate_all(cls, loader: SchemaLoader, out_folder: str):
        print(f"Generating Unity C# classes in {out_folder}/")
        os.makedirs(out_folder, exist_ok=True)

        import glob
        for f in glob.glob(f"{out_folder}/*.cs"): os.remove(f)

        # Compile Jinja Environment
        env = jinja2.Environment(
            loader=jinja2.FileSystemLoader("templates"),
            trim_blocks=True, lstrip_blocks=True
        )
        try:
             template = env.get_template("cs_class3.j2")
        except jinja2.TemplateNotFound:
             print("Warning: templates/cs_class3.j2 missing, skipping dotnet.")
             return

        def write_cs(obj: SchemaObject, wire_obj: bool):
            class_name = pascalcase(obj.name)

            # Format properties specifically for C# rendering
            cs_props = []
            for p_name, p in obj.properties.items():
                cs_type = cls.get_cs_type(p)
                p_dict = {
                     "cs_name": p_name,
                     "cs_type": cs_type,
                     "description": p.description or f"The {p_name} property.",
                     "required": p.required,
                     "default_formatted": cls.format_default(p, cs_type)
                }
                cs_props.append(p_dict)

            out = template.render(
                 obj=obj,
                 wire_obj=wire_obj,
                 cs_class_name=class_name,
                 properties=cs_props
            )

            p_path = os.path.join(out_folder, f"Arena{class_name}Json.cs")
            print(f"-> {p_path}")
            with open(p_path, "w", encoding='utf-8') as f:
                f.write(out)

        for _, obj in loader.arena_objects.items(): write_cs(obj, wire_obj=True)
        for _, obj in loader.components.items(): write_cs(obj, wire_obj=False)

# ---------------------------------------------------------------------------
# CLI Argument Parsing
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="ARENA Schema Builder V3")
    subparsers = parser.add_subparsers(dest="command", help="commands", required=True)

    parser_update = subparsers.add_parser("update", help="Update intermediate schemas")
    parser_update.add_argument("src", help="Source schemas folder")

    parser_docs = subparsers.add_parser("docs", help="Generate Markdown documentation")
    parser_docs.add_argument("--src", help="Source schemas folder (optional, defaults to schemas/)")

    parser_jekyll = subparsers.add_parser("jekyll", help="Generate Jekyll site files")
    parser_jekyll.add_argument("dst", help="Destination folder for Jekyll markdown")
    parser_jekyll.add_argument("--src", help="Source schemas folder (optional, defaults to schemas/)")

    parser_py = subparsers.add_parser("py", help="Update Python class docstrings")
    parser_py.add_argument("dst", help="Destination folder (e.g. arena-py/arena)")
    parser_py.add_argument("--src", help="Source schemas folder (optional, defaults to schemas/)")

    parser_dotnet = subparsers.add_parser("dotnet", help="Generate Unity C# classes")
    parser_dotnet.add_argument("dst", help="Destination folder for C# schemas")
    parser_dotnet.add_argument("--src", help="Source schemas folder (optional, defaults to schemas/)")

    parser_all = subparsers.add_parser("all", help="Run all generators")
    parser_all.add_argument("--src", required=True, help="Source schemas folder")
    parser_all.add_argument("--jekyll-dst", required=True)
    parser_all.add_argument("--py-dst", required=True)
    parser_all.add_argument("--dotnet-dst", required=True)

    args = parser.parse_args()

    # Shared Core Logic (Everything relies on the loaded data model)
    # Docs/Jekyll do not require a separate src for intermediate, they map from the same load tree.
    src_folder = getattr(args, 'src', "schemas")

    loader = SchemaLoader(src_folder)
    loader.build_models()
    print(f"Loaded {len(loader.arena_objects)} ARENA Objects and {len(loader.components)} Components.")

    if args.command == "update":
        print("Writing intermediate schemas...")
        os.makedirs("schemas", exist_ok=True)
        for fn, expanded_json in loader.expanded_cache.items():
             out_path = os.path.join("schemas", os.path.basename(fn))
             with open(out_path, "w", encoding='utf-8') as f:
                 json.dump(expanded_json, f, indent=4)

        list_fns = ["schemas/arena-schema-files.json", "schemas/arena-schema-files-nonpersist.json"]
        for list_fn in list_fns:
             src_path = os.path.join(args.src, list_fn)
             if os.path.exists(src_path):
                 with open(src_path, 'r', encoding='utf-8') as sf:
                     d = json.load(sf)
                 out_path = os.path.join("schemas", os.path.basename(list_fn))
                 with open(out_path, 'w', encoding='utf-8') as df:
                     json.dump(d, df, indent=4)

    elif args.command == "docs":
        MarkdownGenerator.generate_all(loader)

    elif args.command == "jekyll":
        JekyllGenerator.generate_all(loader, args.dst)

    elif args.command == "py":
        PythonGenerator.generate_all(loader, args.dst)

    elif args.command == "dotnet":
        DotnetGenerator.generate_all(loader, args.dst)

    elif args.command == "all":
        # We will do update logic too since `all` needs everything
        print("Running full pipeline...")
        os.makedirs("schemas", exist_ok=True)
        for fn, expanded_json in loader.expanded_cache.items():
             out_path = os.path.join("schemas", os.path.basename(fn))
             with open(out_path, "w", encoding='utf-8') as f:
                 json.dump(expanded_json, f, indent=4)

        list_fns = ["schemas/arena-schema-files.json", "schemas/arena-schema-files-nonpersist.json"]
        for list_fn in list_fns:
             src_path = os.path.join(args.src, list_fn)
             if os.path.exists(src_path):
                 with open(src_path, 'r', encoding='utf-8') as sf:
                     d = json.load(sf)
                 out_path = os.path.join("schemas", os.path.basename(list_fn))
                 with open(out_path, 'w', encoding='utf-8') as df:
                     json.dump(d, df, indent=4)

        MarkdownGenerator.generate_all(loader)
        JekyllGenerator.generate_all(loader, args.jekyll_dst)
        PythonGenerator.generate_all(loader, args.py_dst)
        DotnetGenerator.generate_all(loader, args.dotnet_dst)
        print("Done Docs, Jekyll, Py, and Dotnet.")

if __name__ == "__main__":
    main()
