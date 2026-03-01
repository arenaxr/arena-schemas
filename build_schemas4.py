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
    inline_properties: set = field(default_factory=set)


# We will create a fresh structure
def extract_inline_keys(node: dict) -> set:
    """Helper to find all inline property keys defined in the raw unexpanded schema data block."""
    keys = set()
    if isinstance(node, dict):
        if "properties" in node and isinstance(node["properties"], dict):
            keys.update(node["properties"].keys())
        for k, v in node.items():
            if k != "$ref":
                keys.update(extract_inline_keys(v))
    elif isinstance(node, list):
        for item in node:
            keys.update(extract_inline_keys(item))
    return keys


# ---------------------------------------------------------------------------
# Schema Loader & Resolver
# ---------------------------------------------------------------------------

class SchemaLoader:
    """Loads JSON files, resolves $ref and allOf naturally into dictionaries,
    and converts them to our strict SchemaObject/SchemaProperty dataclasses."""

    def __init__(self, src_folder: str):
        self.src_folder = src_folder
        self._raw_cache = {}    # Cache of raw JSON schemas loaded from disk
        self.arena_objects: Dict[str, SchemaObject] = {}
        self.components: Dict[str, SchemaObject] = {}
        self._wire_object_filenames = set()

    def get_raw(self, filename: str) -> dict:
        filename = os.path.basename(filename)
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
                            resolved = self._resolve_refs(ext_schema, ext_file, ext_schema.get("definitions", {}))
                            if isinstance(resolved, dict): resolved["__orig_ref"] = parts[0].replace(".json", "").split("/")[-1]
                            return resolved

                        curr = ext_schema
                        for p in path: curr = curr.get(p, {})
                        resolved = self._resolve_refs(curr, ext_file, ext_schema.get("definitions", {}))
                        if isinstance(resolved, dict): resolved["__orig_ref"] = path[-1]
                        return resolved
                    else:
                        resolved = self._resolve_refs(ext_schema, ext_file, ext_schema.get("definitions", {}))
                        if isinstance(resolved, dict): resolved["__orig_ref"] = parts[0].replace(".json", "").split("/")[-1]
                        return resolved

                # Internal map ref against local definitions
                else:
                    path = parts[1].strip("/").split("/") # typically ['definitions', 'xyz']
                    if path[0] == "definitions" and path[1] in definitions:
                        # Copy the dict so we don't accidentally mutate definitions
                        resolved = dict(definitions[path[1]])
                        resolved = self._resolve_refs(resolved, base_file, definitions)
                        if isinstance(resolved, dict): resolved["__orig_ref"] = path[1]
                        return resolved

            # standard traversal
            return {k: self._resolve_refs(v, base_file, definitions) for k, v in node.items()}

        else:
            return node

    def build_models(self):
        """Builds expanded JSONs and creates SchemaObjects with strict Wire vs Attribute separation."""
        list_fns = ["arena-schema-files.json", "arena-schema-files-nonpersist.json"]

        # Parse index lists to determine the "Source of Truth" for Wire Objects
        self._wire_object_filenames = set()
        obj_schemas = {}
        for list_fn in list_fns:
            fn_dict = self.get_raw(list_fn)
            obj_schemas.update(fn_dict)
            for key, val in fn_dict.items():
                if isinstance(val, dict) and "file" in val:
                    self._wire_object_filenames.add(val["file"])

        # 1. Parse Top-Level Arena Wire Objects
        for _, obj_info in obj_schemas.items():
            fn = obj_info["file"]
            raw_schema = self.get_raw(fn)
            definitions = raw_schema.get("definitions", {})

            # Expand raw JSON in memory
            expanded = self._resolve_refs(raw_schema, fn, definitions)

            # Data props usually dictate the form of the message
            data_props = expanded.get("properties", {}).get("data", {})
            if "properties" not in data_props:
                continue

            base_name = os.path.splitext(os.path.basename(fn))[0]
            obj_types = data_props.get("properties", {}).get("object_type", {}).get("enum", [])

            # Get inline props before full recursion so we know what's inherently part of the wire object
            raw_data_props = raw_schema.get("properties", {}).get("data", {})
            inline_props = extract_inline_keys(raw_data_props)

            for ot in (obj_types if obj_types else [base_name]):
                obj = self._create_schema_object(ot, data_props)
                obj.is_component = False
                obj.inline_properties = inline_props
                obj.title = expanded.get("title", f"{ot.title()} Data")
                obj.description = expanded.get("description", "")
                self.arena_objects[ot] = obj

        # 2. Discover "components" (Lesser Attributes) simply from the references we just expanded
        # For our purposes, anything that was an object reference or internal object Definition is a component
        # We can re-scan the entire raw cache, and any definitions block or recursively processed refs
        # that are objects should become a Component.

        for fn, raw_schema in self._raw_cache.items():
            # If it's a wire object, its definitions are components
            defs = raw_schema.get("definitions", {})
            if "properties" in raw_schema and "data" in raw_schema["properties"]:
                 defs.update(raw_schema["properties"]["data"].get("definitions", {}))

            for def_name, def_data in defs.items():
                if def_name not in self.components and (def_data.get("type") == "object" or "properties" in def_data):
                    expanded_def = self._resolve_refs(def_data, fn, defs)
                    comp = self._create_schema_object(def_name, expanded_def)
                    comp.is_component = True
                    comp.title = expanded_def.get("title", def_name.title())
                    comp.description = expanded_def.get("description", "")
                    self.components[def_name] = comp

        # 3. Pull out the properties from Wire Objects that are themselves Objects, making them Components
        # Also catch array of objects
        def extract_components_from_props(props: dict, base_dict: dict, fn: str, defs: dict):
            for prop_name, prop_data in props.items():
                if prop_name == "object_type": continue

                is_obj = prop_data.get("type") == "object"
                is_obj_array = prop_data.get("type") == "array" and prop_data.get("items", {}).get("type") == "object"
                has_ref = prop_data.get("$ref") is not None or (prop_data.get("type") == "array" and prop_data.get("items", {}).get("$ref") is not None)
                has_props = "properties" in prop_data or (prop_data.get("type") == "array" and "properties" in prop_data.get("items", {}))

                if is_obj or has_ref or has_props or is_obj_array:

                    target_data = prop_data
                    if prop_data.get("type") == "array":
                        target_data = prop_data.get("items", {})

                    # If this is strictly a reference to a definition, its structural type is that definition.
                    # We shouldn't generate a wrapper component (like "rotationAxis") for it.
                    orig_ref = target_data.get("__orig_ref")
                    ref_path = target_data.get("$ref")
                    if ref_path and not orig_ref:
                         orig_ref = ref_path.split("/")[-1].replace(".json", "").replace("#properties", "")

                    if orig_ref and orig_ref in defs:
                         # We already generated a component for this definition block
                         pass
                    elif prop_name not in self.components:
                        # If this object was already fully expanded by _resolve_refs in the base dict, use that directly
                        expanded_prop = target_data
                        if "__orig_ref" in target_data or "$ref" in target_data:
                            expanded_prop = self._resolve_refs(target_data, fn, defs)

                        # Sometimes references don't have properties directly inside them if they just point
                        if not isinstance(expanded_prop, dict) or ("properties" not in expanded_prop and "type" not in expanded_prop):
                            # Try to see if it's already an expanded component
                            if isinstance(expanded_prop, dict) and len(expanded_prop) > 0 and prop_name != "data":
                                pass
                            else:
                                continue

                        comp = self._create_schema_object(prop_name, expanded_prop)
                        comp.is_component = True
                        comp.title = expanded_prop.get("title", prop_name.title())
                        comp.description = expanded_prop.get("description", "")
                        self.components[prop_name] = comp

                # Recursively look deeper for nested objects like position inside other components
                if isinstance(prop_data, dict) and "properties" in prop_data:
                    extract_components_from_props(prop_data["properties"], base_dict, fn, defs)

        for _, obj in self.arena_objects.items():
             fn = None
             for k, v in obj_schemas.items():
                 if k == obj.name or f"{obj.name} Data" in v.get("title", ""): fn = v["file"]
             if not fn:
                 for f in self._wire_object_filenames:
                      if os.path.splitext(os.path.basename(f))[0] == obj.name: fn = f
             if not fn: continue

             fn = os.path.basename(fn)
             raw_schema = self.get_raw(fn)
             defs = raw_schema.get("definitions", {})

             # Expand the full raw schema to easily traverse all properties and refs
             expanded = self._resolve_refs(raw_schema, fn, defs)
             data_props = expanded.get("properties", {}).get("data", {}).get("properties", {})

             extract_components_from_props(data_props, expanded, fn, defs)

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
            orig_ref = p_data.get("__orig_ref")
            if orig_ref or (t == "object" and "properties" in p_data):
                p_obj.is_ref = True
                p_obj.ref_name = pascalcase(orig_ref if orig_ref else p_name)
                # If we detected an orig_ref, ensure it overwrites the type name
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
        print(f"Generating Python classes in {out_folder}/")
        obj_dir = os.path.join(out_folder, "objects")
        attr_dir = os.path.join(out_folder, "attributes")
        os.makedirs(obj_dir, exist_ok=True)
        os.makedirs(attr_dir, exist_ok=True)

        for name, obj in loader.arena_objects.items():
            cls._write_py_class(obj, obj_dir, is_component=False)
        for name, comp in loader.components.items():
            cls._write_py_class(comp, attr_dir, is_component=True)

    @classmethod
    def _get_py_type(cls, prop: SchemaProperty) -> str:
        t = prop.type_name
        if t == "number": return "float"
        if t == "integer": return "int"
        if t == "boolean": return "bool"
        if t == "string": return "str"
        if t == "array": return "list"
        if t == "object": return "dict"
        return "dict" # Ref types default to dict if not generated explicitly

    @classmethod
    def _generate_docstring(cls, obj: SchemaObject) -> str:
        lines = [f"    \"\"\"\n    {obj.title}"]
        if obj.description:
            lines.append(f"    {obj.description}")
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
            lines.append(f"    :param {py_type} {p_name}: {desc}{req}.{opts_str}{dft_str}")

        lines.append('    \"\"\"')
        return "\n".join(lines)

    @classmethod
    def generate(cls, loader: SchemaLoader, dest_folder: str):
        print(f"Generating Python classes in {dest_folder}/")
        obj_dir = os.path.join(dest_folder, "objects")
        attr_dir = os.path.join(dest_folder, "attributes")
        os.makedirs(obj_dir, exist_ok=True)
        os.makedirs(attr_dir, exist_ok=True)

        for name, obj in loader.arena_objects.items():
             cls._write_py_class(obj, obj_dir, is_component=False)

        for name, comp in loader.components.items():
             cls._write_py_class(comp, attr_dir, is_component=True)

    @classmethod
    def _write_py_class(cls, obj: SchemaObject, folder: str, is_component: bool):
        class_name = pascalcase(obj.name)
        if class_name == "SceneOptions": class_name = "Scene"
        if class_name == "MaterialExtension": class_name = "MaterialExt"

        file_name = f"{snakecase(class_name)}.py"
        target_path = os.path.join(folder, file_name)

        lines = [
            "from dataclasses import dataclass, field",
            "from typing import Optional, List, Dict, Any",
            "",
            f"@dataclass",
            f"class {class_name}:"
        ]

        lines.append(cls._generate_docstring(obj))

        has_props = False
        for p_name, p in obj.properties.items():
            if p_name == "object_type" and not is_component: continue
            has_props = True
            py_type = cls._get_py_type(p)

            # Map required/optional types conceptually
            type_hint = py_type if p.required else f"Optional[{py_type}]"

            if p.default is not None:
                if isinstance(p.default, str):
                    default_val = f"'{p.default}'"
                elif isinstance(p.default, bool):
                    default_val = str(p.default)
                elif isinstance(p.default, (dict, list)):
                    default_val = f"field(default_factory=lambda: {p.default})"
                else:
                    default_val = str(p.default)
                lines.append(f"    {p_name}: {type_hint} = {default_val}")
            else:
                if p.required:
                    lines.append(f"    {p_name}: {type_hint}")
                else:
                    lines.append(f"    {p_name}: {type_hint} = None")

        if not has_props:
            lines.append("    pass")

        lines.append("")

        with open(target_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        print(f"-> {target_path}")

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

        def wordify(txt):
            import num2words
            if txt.isnumeric(): return num2words.num2words(txt)
            return txt

        def enumcase(word):
            if word and word[0:1].isdigit():
                sub_words = re.split(r"(\d+)", word)
                num2worded = "-".join(list(map(wordify, sub_words)))
                return pascalcase(num2worded)
            return pascalcase(word)

        env.globals["enumcase"] = enumcase
        env.globals["pascalcase"] = pascalcase

        def write_cs(obj: SchemaObject, wire_obj: bool):
            class_name = pascalcase(obj.name)

            # Format properties specifically for C# rendering
            cs_props = []
            for p_name, p in obj.properties.items():
                if wire_obj and p_name not in obj.inline_properties:
                    continue
                if p_name == "object_type":
                    continue

                cs_type = cls.get_cs_type(p)
                p_dict = {
                     "name": p_name,
                     "cs_name": pascalcase(p_name),
                     "cs_type": cs_type,
                     "description": p.description or f"The {p_name} property.",
                     "required": p.required,
                     "default_formatted": cls.format_default(p, cs_type),
                     "default": p.default,
                     "deprecated": p.deprecated,
                     "enum": p.enum,
                     "enum_name": f"{pascalcase(p_name)}Type" if p.enum else ""
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
                f.write(f"{out.rstrip()}\n")

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
    parser_docs.add_argument("dst", help="Destination folder for Markdown docs")

    parser_jekyll = subparsers.add_parser("jekyll", help="Generate Jekyll site files")
    parser_jekyll.add_argument("dst", help="Destination folder for Jekyll markdown")

    parser_py = subparsers.add_parser("py", help="Update Python class docstrings")
    parser_py.add_argument("dst", help="Destination folder (e.g. arena-py/arena)")

    parser_dotnet = subparsers.add_parser("dotnet", help="Generate Unity C# classes")
    parser_dotnet.add_argument("dst", help="Destination folder for C# schemas")

    parser_all = subparsers.add_parser("all", help="Run all generators")
    parser_all.add_argument("--src", required=True, help="Source schemas folder")
    parser_all.add_argument("--docs-dst", required=True)
    parser_all.add_argument("--jekyll-dst", required=True)
    parser_all.add_argument("--py-dst", required=True)
    parser_all.add_argument("--dotnet-dst", required=True)

    args = parser.parse_args()

    # Shared Core Logic (Everything relies on the loaded data model)
    # Generators pull strictly from the local schemas folder
    src_folder = "schemas"

    if args.command == "update":
        print(f"Copying schemas from {args.src} to ./schemas...")
        import shutil
        if os.path.exists("schemas"):
            shutil.rmtree("schemas")
        shutil.copytree(args.src, "schemas")
        print("Update complete.")
        return

    # For all other commands, load models from local schemas
    loader = SchemaLoader(src_folder)
    loader.build_models()
    print(f"Loaded {len(loader.arena_objects)} ARENA Objects and {len(loader.components)} Components.")

    if args.command == "docs":
        MarkdownGenerator.generate_all(loader, args.dst)

    elif args.command == "jekyll":
        JekyllGenerator.generate_all(loader, args.dst)

    elif args.command == "py":
        PythonGenerator.generate_all(loader, args.dst)

    elif args.command == "dotnet":
        DotnetGenerator.generate_all(loader, args.dst)

    elif args.command == "all":
        print("Running full pipeline...")
        MarkdownGenerator.generate_all(loader, args.docs_dst)
        JekyllGenerator.generate_all(loader, args.jekyll_dst)
        PythonGenerator.generate_all(loader, args.py_dst)
        DotnetGenerator.generate_all(loader, args.dotnet_dst)
        print("Done Docs, Jekyll, Py, and Dotnet.")

if __name__ == "__main__":
    main()
