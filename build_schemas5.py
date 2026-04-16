#!/usr/bin/env python3
"""ARENA Schema Builder V5 — Full hierarchy with grouped property tables."""
import argparse
import glob
import json
import os
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

import jinja2
from caseconverter import pascalcase, snakecase


# ---------------------------------------------------------------------------
# Data Models
# ---------------------------------------------------------------------------

@dataclass
class SchemaProperty:
    """A single property inside a schema object."""
    name: str
    type_name: str
    description: str = ""
    default: Any = None
    required: bool = False
    is_array: bool = False
    array_item_type: str = ""
    is_ref: bool = False
    ref_name: str = ""        # PascalCase display name
    ref_link: str = ""        # kebab-case link target
    deprecated: bool = False
    enum: List[str] = field(default_factory=list)
    # Language-specific computed fields (populated by compute_language_fields)
    pascal_name: str = ""     # PascalCase of name
    snake_name: str = ""      # snake_case of name
    cs_type: str = ""         # C# type string
    py_type: str = ""         # Python type string
    json_converter: str = ""  # C# JsonConverter attribute


@dataclass
class PropertyGroup:
    """An ordered group of properties from a single source definition."""
    label: str                # Human-readable ("Box", "Entity", "Common", ...)
    source_ref: str = ""      # e.g. "definitions-entity.json" or "" for inline
    property_keys: List[str] = field(default_factory=list)


@dataclass
class SchemaObject:
    """A wire object, component, or envelope."""
    name: str
    title: str = ""
    description: str = ""
    properties: Dict[str, SchemaProperty] = field(default_factory=dict)
    is_component: bool = False
    property_groups: List[PropertyGroup] = field(default_factory=list)
    inline_properties: set = field(default_factory=set)
    definition_group: str = ""   # For components: which group they belong to
    # Language-specific computed fields (populated by compute_language_fields)
    cs_class_name: str = ""   # C# class name (arena- prefix stripped)
    py_class_name: str = ""   # Python class name (with overrides applied)


# ---------------------------------------------------------------------------
# Ref Label Mapping & Helpers
# ---------------------------------------------------------------------------

_REF_LABELS = {
    "definitions-entity": "Entity",
    "definitions-common": "Common",
    "definitions-geometry": "Geometry",
    "definitions-gltf": "GLTF",
}

# Python class name overrides for special cases
_PY_CLASS_NAME_OVERRIDES = {
    "SceneOptions": "Scene",
    "MaterialExtension": "MaterialExt",
}


def _ref_to_label(ref_path: str) -> str:
    """Map a $ref file path to a human-readable group label."""
    base = os.path.splitext(os.path.basename(ref_path))[0]
    # Strip leading ./schemas/ etc.
    base = base.replace("./schemas/", "")
    return _REF_LABELS.get(base, base.replace("definitions-", "").title())


def _ref_to_key(ref_path: str) -> str:
    """Map a $ref file path to a stable key like 'definitions-entity'."""
    base = os.path.splitext(os.path.basename(ref_path))[0]
    return base


def _sanitize_desc(text: str) -> str:
    """Collapse newlines, tabs, and excess whitespace into single spaces."""
    return re.sub(r'\s+', ' ', text).strip() if text else ""


def _strip_arena_prefix(name: str) -> str:
    """Strip 'arena-' prefix from a name to avoid double 'Arena' in class names."""
    if name.startswith("arena-"):
        return name[len("arena-"):]
    return name


def _compute_cs_type(prop: SchemaProperty, known_cs_types: set) -> str:
    """Compute the C# type string for a SchemaProperty."""
    t = prop.type_name
    if prop.is_ref:
        cs = f"Arena{prop.ref_name}Json"
        # Fall back to object if this ref doesn't correspond to a known component
        if known_cs_types and cs not in known_cs_types:
            cs = "object"
    elif t == "number":
        cs = "float?" if prop.default is None else "float"
    elif t == "integer":
        cs = "int?" if prop.default is None else "int"
    elif t == "boolean":
        cs = "bool?" if prop.default is None else "bool"
    elif t == "string":
        cs = "string"
    elif t == "array":
        item_t = prop.array_item_type
        inner = {"number": "float", "integer": "int", "string": "string", "boolean": "bool"}.get(item_t, "object")
        cs = inner
    else:
        cs = "object"
    return f"{cs}[]" if prop.is_array else cs


def _compute_py_type(prop: SchemaProperty) -> str:
    """Compute the Python type string for a SchemaProperty."""
    t = prop.type_name
    if t == "number": return "float"
    if t == "integer": return "int"
    if t == "boolean": return "bool"
    if t == "string": return "str"
    if t == "array": return "list"
    if t == "object": return "dict"
    return "dict"


def _resolve_json_converter(p_name: str, prop: SchemaProperty) -> str:
    """Determine the C# JsonConverter attribute for a property."""
    if isinstance(prop.type_name, list) and "object" in prop.type_name and "boolean" in prop.type_name:
        if prop.is_ref:
            cs_ref = f"Arena{prop.ref_name}Json"
            return f"ArenaBooleanObjectJsonConverter<{cs_ref}>"
    elif prop.is_ref and prop.ref_name == "Vector3":
        return "ArenaVector3JsonConverter"
    elif prop.is_ref and prop.ref_name == "Vector2":
        return "ArenaVector2JsonConverter"
    elif "color" in p_name.lower():
        if prop.is_array:
            return "ArenaColorArrayJsonConverter"
        elif prop.type_name == "string":
            return "ArenaColorJsonConverter"
    return ""


# ---------------------------------------------------------------------------
# Inline Key Extraction (from raw unexpanded schema)
# ---------------------------------------------------------------------------

def extract_inline_keys(node: dict) -> set:
    """Find all inline property keys in a raw schema data block."""
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
    """Loads JSON schemas, resolves $ref/allOf, and builds strict data models
    with property group information for hierarchical docs."""

    def __init__(self, src_folder: str):
        self.src_folder = src_folder
        self._raw_cache: Dict[str, dict] = {}
        self.arena_objects: Dict[str, SchemaObject] = {}
        self.components: Dict[str, SchemaObject] = {}
        self.wire_envelope: Optional[SchemaObject] = None
        self._wire_object_filenames: set = set()
        self._obj_schemas: dict = {}  # name -> {file, title, description}

    # -- File Loading --------------------------------------------------------

    def get_raw(self, filename: str) -> dict:
        filename = os.path.basename(filename)
        if filename not in self._raw_cache:
            path = os.path.join(self.src_folder, filename)
            if not os.path.exists(path):
                print(f"Warning: {filename} missing from {self.src_folder}")
                return {}
            with open(path, "r", encoding="utf-8") as f:
                self._raw_cache[filename] = json.load(f)
        return self._raw_cache[filename]

    # -- $ref / allOf Resolution ---------------------------------------------

    def _resolve_refs(self, node: Any, base_file: str, definitions: dict) -> Any:
        """Deeply resolve JSON $ref and allOf."""
        if isinstance(node, list):
            return [self._resolve_refs(item, base_file, definitions) for item in node]

        if isinstance(node, dict):
            # allOf
            if "allOf" in node:
                new_dict: dict = {}
                for part in node["allOf"]:
                    resolved = self._resolve_refs(part, base_file, definitions)
                    if isinstance(resolved, dict):
                        for k, v in resolved.items():
                            if k not in new_dict:
                                new_dict[k] = {}
                            if isinstance(v, dict) and isinstance(new_dict[k], dict):
                                new_dict[k].update(v)
                            else:
                                new_dict[k] = v
                for k, v in node.items():
                    if k != "allOf":
                        new_dict[k] = self._resolve_refs(v, base_file, definitions)
                return new_dict

            # $ref
            if "$ref" in node:
                ref = node["$ref"]
                parts = ref.split("#")

                # Collect sibling keys (non-$ref) to merge back after resolution
                sibling_keys = {k: v for k, v in node.items() if k != "$ref"}

                if parts[0]:
                    ext_schema = self.get_raw(parts[0])
                    if len(parts) > 1 and parts[1]:
                        path = parts[1].strip("/").split("/")
                        if path == ["properties"]:
                            resolved = self._resolve_refs(
                                ext_schema, parts[0], ext_schema.get("definitions", {})
                            )
                            if isinstance(resolved, dict):
                                resolved["__orig_ref"] = parts[0].replace(".json", "").split("/")[-1]
                            return resolved
                        curr = ext_schema
                        for p in path:
                            curr = curr.get(p, {})
                        resolved = self._resolve_refs(curr, parts[0], ext_schema.get("definitions", {}))
                        if isinstance(resolved, dict):
                            resolved["__orig_ref"] = path[-1]
                        # Merge sibling keys (description, default, etc.) back
                        if isinstance(resolved, dict) and sibling_keys:
                            for sk, sv in sibling_keys.items():
                                if sk not in resolved:
                                    resolved[sk] = sv
                        return resolved
                    else:
                        resolved = self._resolve_refs(
                            ext_schema, parts[0], ext_schema.get("definitions", {})
                        )
                        if isinstance(resolved, dict):
                            resolved["__orig_ref"] = parts[0].replace(".json", "").split("/")[-1]
                        return resolved
                else:
                    path = parts[1].strip("/").split("/")
                    if path[0] == "definitions" and path[1] in definitions:
                        resolved = dict(definitions[path[1]])
                        resolved = self._resolve_refs(resolved, base_file, definitions)
                        if isinstance(resolved, dict):
                            resolved["__orig_ref"] = path[1]
                        # Merge sibling keys back
                        if isinstance(resolved, dict) and sibling_keys:
                            for sk, sv in sibling_keys.items():
                                if sk not in resolved:
                                    resolved[sk] = sv
                        return resolved

            return {k: self._resolve_refs(v, base_file, definitions) for k, v in node.items()}

        return node

    # -- Property Hydration --------------------------------------------------

    def _create_schema_property(self, p_name: str, p_data: dict, required_list: list) -> SchemaProperty:
        """Create a SchemaProperty from raw resolved data."""
        p = SchemaProperty(name=p_name, type_name="object", required=(p_name in required_list))
        raw_desc = p_data.get("description", p_data.get("title", p_name))
        p.description = _sanitize_desc(raw_desc)
        p.default = p_data.get("default")
        p.deprecated = p_data.get("deprecated", False)
        p.enum = p_data.get("enum", [])

        t = p_data.get("type", "object")
        p.type_name = t

        if t == "array":
            p.is_array = True
            items = p_data.get("items", {})
            p.array_item_type = items.get("type", "object")
            items_ref = items.get("__orig_ref")
            if items_ref or (items.get("type") == "object" and "properties" in items):
                p.is_ref = True
                p.ref_name = pascalcase(items_ref if items_ref else p_name)
                p.ref_link = items_ref if items_ref else p_name

        orig_ref = p_data.get("__orig_ref")
        is_obj_type = (t == "object") or (isinstance(t, list) and "object" in t)
        if orig_ref or (is_obj_type and "properties" in p_data):
            p.is_ref = True
            p.ref_name = pascalcase(orig_ref if orig_ref else p_name)
            p.ref_link = orig_ref if orig_ref else p_name
            p.type_name = t if isinstance(t, list) else p.ref_name

        return p

    def _create_schema_object(self, name: str, schema_dict: dict, skip_object_type: bool = True) -> SchemaObject:
        """Hydrate a SchemaObject from a processed schema dict."""
        obj = SchemaObject(name=name)
        required = schema_dict.get("required", [])
        props = schema_dict.get("properties", {})
        for p_name, p_data in props.items():
            if skip_object_type and p_name == "object_type":
                continue
            obj.properties[p_name] = self._create_schema_property(p_name, p_data, required)
        return obj

    # -- Property Group Extraction from raw allOf ----------------------------

    def _extract_property_groups(self, raw_data: dict, obj_title: str) -> List[PropertyGroup]:
        """Walk the raw data.allOf to produce ordered PropertyGroups."""
        groups = []
        all_of = raw_data.get("allOf", [])
        if not all_of:
            # No allOf — all properties are inline
            props = raw_data.get("properties", {})
            keys = [k for k in props if k != "object_type"]
            if keys:
                groups.append(PropertyGroup(label=obj_title, source_ref="", property_keys=keys))
            return groups

        for entry in all_of:
            if "$ref" in entry:
                ref = entry["$ref"]
                ref_file = ref.split("#")[0]
                label = _ref_to_label(ref_file)
                ref_key = _ref_to_key(ref_file)
                # Load the definition file to get its property keys
                raw_def = self.get_raw(ref_file)
                def_props = raw_def.get("properties", {})
                keys = list(def_props.keys())
                if keys:
                    groups.append(PropertyGroup(label=label, source_ref=ref_key, property_keys=keys))
            elif "properties" in entry:
                keys = list(entry["properties"].keys())
                if keys:
                    groups.append(PropertyGroup(label=obj_title, source_ref="", property_keys=keys))

        return groups

    # -- Component Extraction from Wire Object Properties --------------------

    def _extract_components_from_props(self, props, base_dict, fn, defs):
        """Extract component objects from wire object properties (recursive)."""
        for prop_name, prop_data in props.items():
            if prop_name == "object_type":
                continue

            is_obj = prop_data.get("type") == "object"
            is_obj_array = (
                prop_data.get("type") == "array"
                and prop_data.get("items", {}).get("type") == "object"
            )
            has_ref = prop_data.get("$ref") is not None or (
                prop_data.get("type") == "array"
                and prop_data.get("items", {}).get("$ref") is not None
            )
            has_props = "properties" in prop_data or (
                prop_data.get("type") == "array"
                and "properties" in prop_data.get("items", {})
            )

            if is_obj or has_ref or has_props or is_obj_array:
                target_data = prop_data
                if prop_data.get("type") == "array":
                    target_data = prop_data.get("items", {})

                orig_ref = target_data.get("__orig_ref")
                ref_path = target_data.get("$ref")
                if ref_path and not orig_ref:
                    orig_ref = (
                        ref_path.split("/")[-1]
                        .replace(".json", "")
                        .replace("#properties", "")
                        .split("#")[-1]
                    )
                target_name = orig_ref if orig_ref else prop_name

                if target_name not in self.components:
                    expanded_prop = target_data
                    if "__orig_ref" in target_data or "$ref" in target_data:
                        expanded_prop = self._resolve_refs(target_data, fn, defs)
                    if not isinstance(expanded_prop, dict) or (
                        "properties" not in expanded_prop and "type" not in expanded_prop
                    ):
                        if isinstance(expanded_prop, dict) and len(expanded_prop) > 0 and target_name != "data":
                            pass
                        else:
                            continue
                    comp = self._create_schema_object(target_name, expanded_prop)
                    comp.is_component = True
                    comp.title = expanded_prop.get("title", target_name.title())
                    comp.description = _sanitize_desc(expanded_prop.get("description", ""))
                    self.components[target_name] = comp

            if isinstance(prop_data, dict) and "properties" in prop_data:
                self._extract_components_from_props(prop_data["properties"], base_dict, fn, defs)

    # -- Build Models --------------------------------------------------------

    def build_models(self):
        """Main entry point: load all schemas and build the full data model."""
        list_fns = ["arena-schema-files.json", "arena-schema-files-nonpersist.json"]

        self._wire_object_filenames = set()
        self._obj_schemas = {}
        for list_fn in list_fns:
            fn_dict = self.get_raw(list_fn)
            self._obj_schemas.update(fn_dict)
            for key, val in fn_dict.items():
                if isinstance(val, dict) and "file" in val:
                    self._wire_object_filenames.add(val["file"])

        # ── 1. Wire Envelope ──────────────────────────────────────────────
        self._build_wire_envelope()

        # ── 2. Wire Objects ───────────────────────────────────────────────
        obj_schemas = self._obj_schemas
        for _, obj_info in obj_schemas.items():
            fn = obj_info["file"]
            raw_schema = self.get_raw(fn)
            definitions = raw_schema.get("definitions", {})
            expanded = self._resolve_refs(raw_schema, fn, definitions)

            data_props = expanded.get("properties", {}).get("data", {})
            if "properties" not in data_props:
                continue

            base_name = os.path.splitext(os.path.basename(fn))[0]
            obj_types = data_props.get("properties", {}).get("object_type", {}).get("enum", [])

            # Raw data block for group extraction
            raw_data = raw_schema.get("properties", {}).get("data", {})
            if not raw_data and "allOf" in raw_schema:
                for part in raw_schema["allOf"]:
                    if "properties" in part and "data" in part["properties"]:
                        raw_data = part["properties"]["data"]
                        break

            inline_props = extract_inline_keys(raw_data)

            for ot in (obj_types if obj_types else [base_name]):
                obj = self._create_schema_object(ot, data_props, skip_object_type=False)
                obj.is_component = False
                obj.inline_properties = inline_props
                obj.title = expanded.get("title", f"{ot.title()} Data")
                obj.description = _sanitize_desc(expanded.get("description", ""))
                obj.property_groups = self._extract_property_groups(raw_data, obj.title)
                self.arena_objects[ot] = obj

        # Add data links to envelope now that all objects are loaded
        self._add_data_links_to_envelope()

        # ── 3. Components from definitions blocks ─────────────────────────
        # Track which definition group each component belongs to
        def_group_map = {}  # component_name → group label

        for fn, raw_schema in self._raw_cache.items():
            defs = raw_schema.get("definitions", {})
            if "properties" in raw_schema and "data" in raw_schema["properties"]:
                defs.update(raw_schema["properties"]["data"].get("definitions", {}))

            ref_key = _ref_to_key(fn)
            group_label = _REF_LABELS.get(ref_key, "")

            for def_name, def_data in defs.items():
                if def_name not in self.components and (
                    def_data.get("type") == "object" or "properties" in def_data
                ):
                    expanded_def = self._resolve_refs(def_data, fn, defs)
                    comp = self._create_schema_object(def_name, expanded_def)
                    comp.is_component = True
                    comp.title = expanded_def.get("title", def_name.title())
                    comp.description = _sanitize_desc(expanded_def.get("description", ""))
                    if group_label:
                        comp.definition_group = group_label
                        def_group_map[def_name] = group_label
                    self.components[def_name] = comp

        # ── 4. Components from Wire Object properties ─────────────────────
        for _, obj in self.arena_objects.items():
            fn = None
            for k, v in obj_schemas.items():
                if k == obj.name or f"{obj.name} Data" in v.get("title", ""):
                    fn = v["file"]
            if not fn:
                for f in self._wire_object_filenames:
                    if os.path.splitext(os.path.basename(f))[0] == obj.name:
                        fn = f
            if not fn:
                continue

            fn = os.path.basename(fn)
            raw_schema = self.get_raw(fn)
            defs = raw_schema.get("definitions", {})
            expanded = self._resolve_refs(raw_schema, fn, defs)
            data_props = expanded.get("properties", {}).get("data", {}).get("properties", {})
            self._extract_components_from_props(data_props, expanded, fn, defs)

    # -- Wire Envelope ──────────────────────────────────────────────────────

    def _build_wire_envelope(self):
        """Build a merged wire envelope SchemaObject from all message type definitions."""
        # Collect properties from the different envelope definitions
        envelope_sources = [
            ("definitions-arena-object.json", "object"),
            ("definitions-arena-event.json", "event"),
        ]
        # Also pull top-level properties from program and scene-options
        program_sources = [
            ("program.json", "program"),
            ("scene-options.json", "scene-options"),
        ]

        merged_props: Dict[str, dict] = {}
        all_required: set = set()

        for fn, type_val in envelope_sources:
            raw = self.get_raw(fn)
            for pname, pdata in raw.get("properties", {}).items():
                if pname == "type":
                    # Merge type enums
                    if pname in merged_props:
                        existing_enum = merged_props[pname].get("enum", [])
                        new_enum = pdata.get("enum", [])
                        merged_props[pname]["enum"] = list(set(existing_enum + new_enum))
                    else:
                        merged_props[pname] = dict(pdata)
                        merged_props[pname]["description"] = "ARENA message type."
                elif pname not in merged_props:
                    merged_props[pname] = dict(pdata)

        for fn, type_val in program_sources:
            raw = self.get_raw(fn)
            for pname, pdata in raw.get("properties", {}).items():
                if pname == "data":
                    continue  # Skip data — documented per-type
                if pname == "type":
                    if pname in merged_props:
                        existing_enum = merged_props[pname].get("enum", [])
                        new_enum = pdata.get("enum", [])
                        merged_props[pname]["enum"] = list(set(existing_enum + new_enum))
                    else:
                        merged_props[pname] = dict(pdata)
                elif pname not in merged_props:
                    merged_props[pname] = dict(pdata)
            all_required.update(raw.get("required", []))

        # Build SchemaObject
        required_list = list(all_required)
        envelope = SchemaObject(name="arena-message")
        envelope.title = "ARENA Message"
        envelope.description = (
            "The top-level ARENA wire message. All ARENA messages share this envelope structure. "
            "The `data` attribute contents depend on the message `type`."
        )

        for pname, pdata in merged_props.items():
            if pname == "data":
                continue
            envelope.properties[pname] = self._create_schema_property(pname, pdata, required_list)

        # Sort type enum
        if "type" in envelope.properties and envelope.properties["type"].enum:
            envelope.properties["type"].enum = sorted(envelope.properties["type"].enum)

        self.wire_envelope = envelope

    def _add_data_links_to_envelope(self):
        """Add a 'data' property to the wire envelope that links to all wire object types."""
        if not self.wire_envelope:
            return

        # Build a list of links to all wire object data pages
        links = []
        for name in sorted(self.arena_objects.keys()):
            obj = self.arena_objects[name]
            links.append(f"[{obj.title}]({name})")

        links_str = ", ".join(links)
        data_prop = SchemaProperty(
            name="data",
            type_name="object",
            description=f"The message payload. Varies by message type. See: {links_str}",
            required=True,
        )
        self.wire_envelope.properties["data"] = data_prop

    # -- Language Field Computation ------------------------------------------

    def compute_language_fields(self):
        """Populate language-specific fields on all properties and objects."""
        # Build known C# type set from all objects and components
        known_cs_types = {"ArenaVector3Json", "ArenaVector2Json"}
        all_objects = list(self.arena_objects.values()) + list(self.components.values())
        for obj in all_objects:
            stripped = _strip_arena_prefix(obj.name)
            known_cs_types.add(f"Arena{pascalcase(stripped)}Json")

        # Process all objects including wire envelope
        all_to_process = all_objects[:]
        if self.wire_envelope:
            all_to_process.append(self.wire_envelope)

        for obj in all_to_process:
            # Object-level class names
            stripped = _strip_arena_prefix(obj.name)
            obj.cs_class_name = pascalcase(stripped)
            py_name = pascalcase(obj.name)
            obj.py_class_name = _PY_CLASS_NAME_OVERRIDES.get(py_name, py_name)

            # Property-level fields
            for p_name, p in obj.properties.items():
                p.pascal_name = pascalcase(p_name)
                p.snake_name = snakecase(p_name)
                p.cs_type = _compute_cs_type(p, known_cs_types)
                p.py_type = _compute_py_type(p)
                p.json_converter = _resolve_json_converter(p_name, p)


# ---------------------------------------------------------------------------
# Markdown Generator
# ---------------------------------------------------------------------------

class MarkdownGenerator:
    """Generates markdown docs with grouped property tables."""

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
    def generate_table(cls, obj: SchemaObject, only_keys: List[str] = None) -> str:
        """Generate a markdown table. If only_keys is provided, only include those properties."""
        lines = [
            "| Attribute | Type | Default | Description | Required |",
            "| :--- | :--- | :--- | :--- | :--- |",
        ]

        props_to_render = obj.properties.items()
        if only_keys is not None:
            props_to_render = [(k, obj.properties[k]) for k in only_keys if k in obj.properties]

        for p_name, p in props_to_render:
            req = "Yes" if p.required else "No"
            type_str = p.type_name
            desc_str = (p.description or p_name).replace("\n", " ")
            dft_str = cls.format_value(p) if p.default is not None else ""

            if p.is_ref:
                type_str = f"[{p.ref_name}]({p.ref_link})"
            if p.is_array:
                if p.is_ref:
                    type_str = f"[{p.ref_name}]({p.ref_link})[]"
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
    def _render_page_body(cls, obj: SchemaObject, page_type: str) -> List[str]:
        """Render the body content for a schema page (shared by Markdown and Jekyll)."""
        lines = []
        if page_type == "envelope":
            lines.append(f"{obj.description}\n")
            lines.append(f"## {obj.title} Attributes\n")
            lines.append(cls.generate_table(obj))
            lines.append("\n")

        elif page_type == "wire_object":
            schema_desc = f"This is the schema for {obj.title}, the properties of wire object type `{obj.name}`."
            lines.append(f"{obj.description}\n\n{schema_desc}\n")
            lines.append(
                "All wire objects have a set of basic attributes "
                "`{object_id, action, type, persist, data}`. "
                "The `data` attribute defines the object-specific attributes\n"
            )
            if obj.property_groups:
                for group in obj.property_groups:
                    keys_in_obj = [k for k in group.property_keys if k in obj.properties]
                    if not keys_in_obj:
                        continue
                    lines.append(f"### {group.label} Properties\n")
                    lines.append(cls.generate_table(obj, only_keys=keys_in_obj))
                    lines.append("\n")
            else:
                lines.append(f"## {obj.title} Attributes\n")
                lines.append(cls.generate_table(obj))
                lines.append("\n")

        elif page_type == "component":
            schema_desc = f"This is the schema for {obj.title}, the properties of object `{obj.name}`."
            if obj.definition_group:
                schema_desc += f" Part of the **{obj.definition_group}** definition set."
            lines.append(f"{obj.description}\n\n{schema_desc}\n")
            lines.append(f"## {obj.title} Attributes\n")
            lines.append(cls.generate_table(obj))
            lines.append("\n")

        return lines

    @classmethod
    def generate_all(cls, loader: SchemaLoader, out_folder: str = "docs"):
        """Generate all markdown docs."""
        print(f"Generating markdown docs to {out_folder}/")
        os.makedirs(out_folder, exist_ok=True)
        for f in glob.glob(f"{out_folder}/*.md"):
            os.remove(f)

        # Wire Envelope
        if loader.wire_envelope:
            cls._write_envelope_md(loader.wire_envelope, out_folder)

        # Wire Objects (grouped tables)
        for _, obj in loader.arena_objects.items():
            cls._write_wire_object_md(obj, out_folder)

        # Components (single table)
        for _, obj in loader.components.items():
            cls._write_component_md(obj, out_folder)

    @classmethod
    def _write_envelope_md(cls, obj: SchemaObject, out_folder: str):
        md = [f"# `{obj.name}`\n"]
        md.extend(cls._render_page_body(obj, "envelope"))

        p_path = os.path.join(out_folder, f"{obj.name}.md")
        print(f"-> {p_path}")
        with open(p_path, "w", encoding="utf-8") as f:
            f.write("\n".join(md))

    @classmethod
    def _write_wire_object_md(cls, obj: SchemaObject, out_folder: str):
        md = [f"# `{obj.name}`\n"]
        md.extend(cls._render_page_body(obj, "wire_object"))

        p_path = os.path.join(out_folder, f"{obj.name}.md")
        print(f"-> {p_path}")
        with open(p_path, "w", encoding="utf-8") as f:
            f.write("\n".join(md))

    @classmethod
    def _write_component_md(cls, obj: SchemaObject, out_folder: str):
        md = [f"# `{obj.name}`\n"]
        md.extend(cls._render_page_body(obj, "component"))

        p_path = os.path.join(out_folder, f"{obj.name}.md")
        print(f"-> {p_path}")
        with open(p_path, "w", encoding="utf-8") as f:
            f.write("\n".join(md))


# ---------------------------------------------------------------------------
# Jekyll Generator
# ---------------------------------------------------------------------------

class JekyllGenerator:
    """Generates Jekyll-formatted markdown with YAML front matter."""

    @classmethod
    def generate_all(cls, loader: SchemaLoader, out_folder: str):
        print(f"Generating Jekyll site to {out_folder}/")
        os.makedirs(out_folder, exist_ok=True)
        for f in glob.glob(f"{out_folder}/*.md"):
            os.remove(f)

        sec_title = "ARENA Objects"
        sec_sub_title = "Objects Schema"

        # Index page
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
            "| :--- | :--- |",
        ]
        for name, obj in sorted(loader.arena_objects.items()):
            desc_line = obj.description.splitlines()[0] if obj.description else ""
            index_md.append(f"|[{obj.title}]({name})|{desc_line}|")

        index_path = os.path.join(out_folder, "index.md")
        with open(index_path, "w", encoding="utf-8") as f:
            f.write("\n".join(index_md) + "\n")

        # Wire envelope page
        if loader.wire_envelope:
            cls._write_page(
                loader.wire_envelope, sec_title, sec_sub_title, out_folder,
                page_type="envelope", loader=loader,
            )

        # Wire object pages
        for _, obj in loader.arena_objects.items():
            cls._write_page(
                obj, sec_title, sec_sub_title, out_folder,
                page_type="wire_object", loader=loader,
            )

        # Component pages
        for _, obj in loader.components.items():
            cls._write_page(
                obj, sec_title, sec_sub_title, out_folder,
                page_type="component", loader=loader,
            )

    @classmethod
    def _write_page(
        cls, obj: SchemaObject, sec_title: str, sec_sub_title: str,
        out_folder: str, page_type: str, loader: SchemaLoader = None,
    ):
        page_md = [
            "---",
            f"title: {obj.name}",
            "layout: default",
            f"parent: {sec_sub_title}",
            f"grand_parent: {sec_title}",
            "---",
            "\n<!--CAUTION: This file is autogenerated from https://github.com/arenaxr/arena-schemas. Changes made here may be overwritten.-->\n",
            f"# `{obj.name}`\n",
        ]

        page_md.extend(MarkdownGenerator._render_page_body(obj, page_type))

        out_path = os.path.join(out_folder, f"{obj.name}.md")
        print(f"-> {out_path}")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write("\n".join(page_md))


# ---------------------------------------------------------------------------
# Python Generator
# ---------------------------------------------------------------------------

class PythonGenerator:
    """Generates Python dataclass files using Jinja2 templates."""

    @classmethod
    def generate_all(cls, loader: SchemaLoader, out_folder: str):
        print(f"Generating Python classes in {out_folder}/")
        obj_dir = os.path.join(out_folder, "objects")
        attr_dir = os.path.join(out_folder, "attributes")
        os.makedirs(obj_dir, exist_ok=True)
        os.makedirs(attr_dir, exist_ok=True)

        env = jinja2.Environment(
            loader=jinja2.FileSystemLoader("templates"),
            trim_blocks=True, lstrip_blocks=True,
        )
        try:
            template = env.get_template("py_class.j2")
        except jinja2.TemplateNotFound:
            print("Warning: templates/py_class.j2 missing, skipping python.")
            return

        for name, obj in loader.arena_objects.items():
            cls._write_py_class(obj, obj_dir, is_component=False, template=template)
        for name, comp in loader.components.items():
            cls._write_py_class(comp, attr_dir, is_component=True, template=template)

    @classmethod
    def _build_py_context(cls, obj: SchemaObject, is_component: bool) -> dict:
        """Build template context for Python class generation."""
        properties = []
        for p_name, p in obj.properties.items():
            if not is_component and p_name not in obj.inline_properties:
                continue

            # Compute type hint
            type_hint = p.py_type if p.required else f"Optional[{p.py_type}]"

            # Compute default value string
            if p.default is not None:
                if isinstance(p.default, str):
                    default_str = f"'{p.default}'"
                elif isinstance(p.default, bool):
                    default_str = str(p.default)
                elif isinstance(p.default, (dict, list)):
                    default_str = f"field(default_factory=lambda: {p.default})"
                else:
                    default_str = str(p.default)
            elif p.required:
                default_str = None  # No default for required fields
            else:
                default_str = "None"

            # Compute docstring param line
            req_str = "" if p.required else ", optional"
            dft_doc = ""
            if p.default is not None:
                dft_doc = f" Defaults to {p.default}"
                if p.type_name == "string":
                    dft_doc = f" Defaults to '{p.default}'"
            opts_doc = ""
            if p.enum:
                if len(p.enum) == 1:
                    opts_doc = f" Must be '{p.enum[0]}'."
                else:
                    opts_doc = f" Allows {p.enum}."
            desc = p.description or p_name
            param_line = f":param {p.py_type} {p_name}: {desc}{req_str}.{opts_doc}{dft_doc}"

            properties.append({
                "name": p_name,
                "type_hint": type_hint,
                "default_str": default_str,
                "param_line": param_line,
            })

        return {
            "class_name": obj.py_class_name,
            "title": obj.title,
            "description": obj.description,
            "properties": properties,
        }

    @classmethod
    def _write_py_class(cls, obj: SchemaObject, folder: str, is_component: bool, template):
        file_name = f"{snakecase(obj.py_class_name)}.py"
        target_path = os.path.join(folder, file_name)

        context = cls._build_py_context(obj, is_component)
        out = template.render(**context)

        with open(target_path, "w", encoding="utf-8") as f:
            f.write(f"{out.rstrip()}\n")
        print(f"-> {target_path}")


# ---------------------------------------------------------------------------
# Dotnet Generator
# ---------------------------------------------------------------------------

class DotnetGenerator:
    """Generates Unity C# classes using Jinja2 templates."""

    @classmethod
    def _format_cs_value(cls, val) -> str:
        """Format a Python value as a C# literal for object initializers."""
        if isinstance(val, bool):
            return str(val).lower()
        if isinstance(val, float) or isinstance(val, int):
            return f"{val}f"
        if isinstance(val, str):
            return f'"{val}"'
        if isinstance(val, dict):
            # Nested object — not handled, fall back
            return "null"
        return str(val)

    @classmethod
    def format_default(cls, prop: SchemaProperty) -> str:
        """Format a property's default value as a C# literal."""
        d = prop.default
        if d is None:
            return ""
        cs_type = prop.cs_type
        if isinstance(d, bool):
            return str(d).lower()
        if isinstance(d, list):
            # Array initializer — use shorthand { items }
            base_type = cs_type.rstrip("[]")
            if not d:
                return "{  }"
            # Complex items (dicts) — object initializer
            if any(isinstance(item, dict) for item in d):
                obj_inits = []
                for item in d:
                    props = ", ".join(f"{pascalcase(k)} = {cls._format_cs_value(v)}" for k, v in item.items())
                    obj_inits.append(f"new() {{ {props} }}")
                return f"{{ {', '.join(obj_inits)} }}"
            if base_type == "float":
                items = ", ".join(f"{x}f" for x in d)
            elif base_type == "string":
                items = ", ".join(f'"{x}"' for x in d)
            else:
                items = ", ".join(str(x) for x in d)
            return f"{{ {items} }}"
        if isinstance(d, dict):
            props = ", ".join(f"{pascalcase(k)} = {cls._format_cs_value(v)}" for k, v in d.items())
            return f"new() {{ {props} }}"
        if cs_type in ("float", "float?", "float[]", "float?[]"):
            return f"{d}f"
        if cs_type in ("string",):
            return f'"{d}"'
        return str(d)

    @classmethod
    def _build_cs_prop_dict(cls, p_name: str, p: SchemaProperty, desc_fallback: str = None) -> dict:
        """Build a unified property dict for C# Jinja2 template rendering."""
        description = p.description or (desc_fallback if desc_fallback else p_name)

        bool_object_converter = ""
        if p.is_ref and p_name in ("click-listener",):
            bool_object_converter = f"ArenaBooleanObjectJsonConverter<{p.cs_type}>"

        return {
            "name": p_name,
            "cs_name": p.pascal_name,
            "cs_type": p.cs_type,
            "description": description,
            "required": p.required,
            "default_formatted": cls.format_default(p),
            "default": p.default,
            "deprecated": p.deprecated,
            "enum": p.enum,
            "enum_name": f"{p.pascal_name}Type" if p.enum else "",
            "is_ref": p.is_ref,
            "json_converter": p.json_converter,
            "bool_object_converter": bool_object_converter,
        }

    @classmethod
    def generate_all(cls, loader: SchemaLoader, out_folder: str):
        print(f"Generating Unity C# classes in {out_folder}/")
        obj_dir = os.path.join(out_folder, "Object")
        attr_dir = os.path.join(out_folder, "Attribute")
        os.makedirs(obj_dir, exist_ok=True)
        os.makedirs(attr_dir, exist_ok=True)
        # Only clean the subdirectories we manage
        for f in glob.glob(f"{obj_dir}/*.cs"):
            os.remove(f)
        for f in glob.glob(f"{attr_dir}/*.cs"):
            os.remove(f)

        env = jinja2.Environment(
            loader=jinja2.FileSystemLoader("templates"),
            trim_blocks=True, lstrip_blocks=True,
        )
        try:
            template = env.get_template("cs_class3.j2")
        except jinja2.TemplateNotFound:
            print("Warning: templates/cs_class3.j2 missing, skipping dotnet.")
            return

        import num2words

        def wordify(txt):
            if txt.isnumeric():
                return num2words.num2words(txt)
            return txt

        def enumcase(word):
            if word and word[0:1].isdigit():
                sub_words = re.split(r"(\d+)", word)
                num2worded = "-".join(list(map(wordify, sub_words)))
                return pascalcase(num2worded)
            return pascalcase(word)

        env.globals["enumcase"] = enumcase
        env.globals["pascalcase"] = pascalcase

        def write_cs(obj: SchemaObject, wire_obj: bool, target_dir: str):
            class_name = obj.cs_class_name

            # Determine which properties belong directly to this object
            allowed_props = set(obj.properties.keys())
            if wire_obj:
                allowed_props = set()
                for group in obj.property_groups:
                    # Generic entity/common stuff shouldn't generate fields on the wire object
                    # We only want inline properties or properties from the specific object's definition
                    if not group.source_ref:
                        allowed_props.update(group.property_keys)
                    elif group.source_ref == f"{obj.name}":
                        allowed_props.update(group.property_keys)

            cs_props = []
            for p_name, p in obj.properties.items():
                if p_name not in allowed_props:
                    continue
                if wire_obj and p_name == "object_type":
                    continue  # handled by readonly field in template
                cs_props.append(cls._build_cs_prop_dict(p_name, p, desc_fallback=f"The {p_name} property."))

            uses_converter = any(cp["json_converter"] for cp in cs_props)
            out = template.render(
                obj=obj, wire_obj=wire_obj,
                cs_class_name=class_name, properties=cs_props,
                uses_converter=uses_converter,
            )
            p_path = os.path.join(target_dir, f"Arena{class_name}Json.cs")
            print(f"-> {p_path}")
            with open(p_path, "w", encoding="utf-8") as f:
                f.write(f"{out.rstrip()}\n")

        # Build set of component class names to detect collisions
        component_class_names = {obj.cs_class_name for _, obj in loader.components.items()}

        # Wire objects → Object/ subdirectory (skip if class name collides with component)
        for _, obj in loader.arena_objects.items():
            if obj.cs_class_name in component_class_names:
                print(f"   (skipping Object/{obj.cs_class_name} — collides with Attribute component)")
                continue
            write_cs(obj, wire_obj=True, target_dir=obj_dir)
        # Components → Attribute/ subdirectory
        for _, obj in loader.components.items():
            write_cs(obj, wire_obj=False, target_dir=attr_dir)

        # Generate data wrapper files in the root output folder
        cls._generate_data_object(loader, out_folder, env)
        cls._generate_data_scene_options(loader, out_folder, env)
        cls._generate_message(loader, out_folder, env)

    @classmethod
    def _generate_data_object(cls, loader: SchemaLoader, out_folder: str, env: jinja2.Environment):
        """Generate ArenaDataObjectJson.cs — data wrapper for type:'object' messages."""
        try:
            tmpl = env.get_template("cs_data_object.j2")
        except jinja2.TemplateNotFound:
            print("Warning: templates/cs_data_object.j2 missing, skipping data object.")
            return

        # Derive definition sources from _REF_LABELS (single source of truth)
        def_sources = [(f"{key}.json", label) for key, label in _REF_LABELS.items()]
        def_key_sets = {}
        for def_file, label in def_sources:
            raw = loader.get_raw(def_file)
            def_key_sets[label] = set(raw.get("properties", {}).keys())

        # Use the entity wire object (broadest set) to gather all properties
        entity_obj = loader.arena_objects.get("entity")
        if not entity_obj:
            print("Warning: 'entity' not found in arena_objects, skipping data object.")
            return

        # Group properties by definition source
        property_groups = []
        seen = set()

        # First: object_type is special (handled inline in template, not in groups)

        # Inline properties (those not from any definition file)
        inline_props = []
        for p_name, p in entity_obj.properties.items():
            if p_name == "object_type":
                continue
            is_from_def = any(p_name in keys for keys in def_key_sets.values())
            if not is_from_def and p_name in entity_obj.inline_properties:
                inline_props.append(cls._build_cs_prop_dict(p_name, p))
                seen.add(p_name)

        # Definition-sourced groups
        for _, label in def_sources:
            group_props = []
            for p_name in def_key_sets.get(label, []):
                if p_name in seen or p_name == "object_type":
                    continue
                if p_name in entity_obj.properties:
                    group_props.append(cls._build_cs_prop_dict(p_name, entity_obj.properties[p_name]))
                    seen.add(p_name)
            if group_props:
                property_groups.append({"label": label, "properties": group_props})


        all_props = inline_props[:]
        for g in property_groups:
            all_props.extend(g["properties"])

        uses_converter = any(dp.get("json_converter") or dp.get("bool_object_converter") for dp in all_props)
        out = tmpl.render(
            inline_properties=inline_props,
            property_groups=property_groups,
            uses_converter=uses_converter,
        )
        p_path = os.path.join(out_folder, "ArenaDataObjectJson.cs")
        print(f"-> {p_path}")
        with open(p_path, "w", encoding="utf-8") as f:
            f.write(f"{out.rstrip()}\n")

    @classmethod
    def _generate_data_scene_options(cls, loader: SchemaLoader, out_folder: str, env: jinja2.Environment):
        """Generate ArenaDataSceneOptionsJson.cs — data wrapper for type:'scene-options' messages."""
        try:
            tmpl = env.get_template("cs_data_scene_options.j2")
        except jinja2.TemplateNotFound:
            print("Warning: templates/cs_data_scene_options.j2 missing, skipping data scene options.")
            return

        # Get the scene-options wire object and extract its component-ref properties
        # Try both possible keys: the schema filename-based key and the object_type key
        scene_obj = loader.arena_objects.get("arena-scene-options") or loader.arena_objects.get("scene-options")
        if not scene_obj:
            print("Warning: 'scene-options'/'arena-scene-options' not found in arena_objects, skipping.")
            return

        data_props = []
        for p_name, p in scene_obj.properties.items():
            if p_name == "object_type":
                continue
            data_props.append(cls._build_cs_prop_dict(p_name, p))

        out = tmpl.render(properties=data_props)
        p_path = os.path.join(out_folder, "ArenaDataSceneOptionsJson.cs")
        print(f"-> {p_path}")
        with open(p_path, "w", encoding="utf-8") as f:
            f.write(f"{out.rstrip()}\n")

    @classmethod
    def _generate_message(cls, loader: SchemaLoader, out_folder: str, env: jinja2.Environment):
        """Generate ArenaMessageJson.cs — the MQTT wire envelope."""
        try:
            tmpl = env.get_template("cs_message.j2")
        except jinja2.TemplateNotFound:
            print("Warning: templates/cs_message.j2 missing, skipping message.")
            return

        if not loader.wire_envelope:
            print("Warning: wire envelope not built, skipping message generation.")
            return

        msg_props = []
        for p_name, p in loader.wire_envelope.properties.items():
            if p_name == "data":
                continue  # data is handled specially in the template
            msg_props.append({
                "name": p_name,
                "cs_type": p.cs_type,
            })

        out = tmpl.render(properties=msg_props)
        p_path = os.path.join(out_folder, "ArenaMessageJson.cs")
        print(f"-> {p_path}")
        with open(p_path, "w", encoding="utf-8") as f:
            f.write(f"{out.rstrip()}\n")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="ARENA Schema Builder V5")
    subparsers = parser.add_subparsers(dest="command", help="commands", required=True)

    sub_update = subparsers.add_parser("update", help="Copy schemas from source")
    sub_update.add_argument("src", help="Source schemas folder")

    sub_docs = subparsers.add_parser("docs", help="Generate Markdown documentation")
    sub_docs.add_argument("dst", help="Destination folder")

    sub_jekyll = subparsers.add_parser("jekyll", help="Generate Jekyll site files")
    sub_jekyll.add_argument("dst", help="Destination folder")

    sub_py = subparsers.add_parser("py", help="Generate Python classes")
    sub_py.add_argument("dst", help="Destination folder")

    sub_dotnet = subparsers.add_parser("dotnet", help="Generate Unity C# classes")
    sub_dotnet.add_argument("dst", help="Destination folder")

    sub_all = subparsers.add_parser("all", help="Run all generators")
    sub_all.add_argument("--src", required=True)
    sub_all.add_argument("--docs-dst", required=True)
    sub_all.add_argument("--jekyll-dst", required=True)
    sub_all.add_argument("--py-dst", required=True)
    sub_all.add_argument("--dotnet-dst", required=True)

    args = parser.parse_args()
    src_folder = "schemas"

    if args.command == "update":
        import shutil
        print(f"Copying schemas from {args.src} to ./schemas...")
        if os.path.exists("schemas"):
            shutil.rmtree("schemas")
        shutil.copytree(args.src, "schemas")
        print("Update complete.")
        return

    loader = SchemaLoader(src_folder)
    loader.build_models()
    loader.compute_language_fields()
    print(
        f"Loaded {len(loader.arena_objects)} ARENA Objects "
        f"and {len(loader.components)} Components."
    )

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
        print("Done.")


if __name__ == "__main__":
    main()
