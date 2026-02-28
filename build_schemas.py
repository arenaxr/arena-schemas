import argparse
import collections
import glob
import json
import os
import re
import sys

import jinja2
import num2words
from caseconverter import pascalcase, snakecase
from mdutils.mdutils import MdUtils

ObjTypeDesc = {
    "object": "AFrame 3D Object",
    "program": "ARENA program data",
    "scene-options": "ARENA scene options",
    "landmarks": "ARENA landmarks",
    "camera-override": "ARENA camera override data",
}

# ---------------------------------------------------------------------------
# Common Helpers
# ---------------------------------------------------------------------------

def get_prop(prop, key):
    if key in prop:
        return prop[key]
    else:
        return None

def definition_py_cs(name, prop):
    title = get_prop(prop, "title")
    description = get_prop(prop, "description")
    if description:
        return description.replace("\n", " ").replace("  ", " ")
    elif title:
        return title
    else:
        return name

def parse_allof_ref(allof_schema, input_folder, expand_refs=True, attr_classes=None, obj_attr_schema=None):
    if attr_classes is None:
        attr_classes = {}
    if obj_attr_schema is None:
        obj_attr_schema = {}

    new_schema = allof_schema
    for props in allof_schema["allOf"]:
        for key in props:
            if key == "$ref":
                ref = props[key].split("#")
                key = ref[1].replace("/", "") if len(ref) > 1 else ref[0].split("/")[-1].replace(".json", "")

                # Check if it was empty after the '#/' or '#' (we want the filename without extension as fallback)
                if not key:
                    key = ref[0].split("/")[-1].replace(".json", "")

                with open(os.path.join(input_folder, ref[0])) as f:
                    sub_schema = json.load(f)
                if expand_refs:
                    props = sub_schema
                else:
                    for prop in sub_schema.get("properties", {}):
                        attr_class = pascalcase(prop)
                        attr_ns = snakecase(prop)
                        obj_attr_schema[prop] = sub_schema["properties"][prop]
                        if "properties" in sub_schema["properties"][prop]:
                            attr_classes[attr_ns] = attr_class
                        else:
                            attr_classes[attr_ns] = None
                    continue

            if key not in new_schema:
                new_schema[key] = {}
            new_schema[key].update(props[key])
    return new_schema

# ---------------------------------------------------------------------------
# Updateschemas (update)
# ---------------------------------------------------------------------------

def cmd_update(args):
    input_folder = args.src
    output_folder = "schemas"
    list_fns = ["schemas/arena-schema-files.json", "schemas/arena-schema-files-nonpersist.json"]

    obj_schemas = {}
    for list_fn in list_fns:
        obj_schema_path = os.path.join(input_folder, list_fn)
        with open(obj_schema_path) as f:
            obj_schemas.update(json.load(f))
        for _, obj_schema in obj_schemas.items():
            fn = obj_schema["file"]
            with open(os.path.join(input_folder, fn)) as f:
                schema = json.load(f)

            # resolve references
            if "allOf" in schema:
                new_schema = parse_allof_ref(schema, input_folder)
                del schema["allOf"]
            else:
                new_schema = schema
            if "allOf" in new_schema["properties"]["data"]:
                new_schema["properties"]["data"] = parse_allof_ref(new_schema["properties"]["data"], input_folder)
                del new_schema["properties"]["data"]["allOf"]

            # generate definitions
            if "definitions" not in new_schema:
                new_schema["definitions"] = {}
            if "data" in new_schema["properties"] and "properties" in new_schema["properties"]["data"]:
                dprops = new_schema["properties"]["data"]["properties"]
                for key in dprops:
                    if "type" in dprops[key] and dprops[key]["type"] == "object" and "deprecated" not in dprops[key]:
                        if key not in new_schema["definitions"]:
                            new_schema["definitions"][key] = dprops[key]
                            new_schema["properties"]["data"]["properties"][key] = {"$ref": f"#/definitions/{key}"}

            # write this object expanded json schema
            new_obj_json = json.dumps(new_schema, indent=4)
            file = open(os.path.join(output_folder, fn[8:]), "w")
            file.write(new_obj_json)
            file.close()

    # write object list
    file = open(os.path.join(output_folder, "arena-schema-files.json"), "w")
    file.write(json.dumps(obj_schemas, indent=4))
    file.close()


# ---------------------------------------------------------------------------
# Main (main)
# ---------------------------------------------------------------------------

def cmd_main(args):
    arena_objects_schema_path = "schemas/input/arena-obj3d.json"
    obj_schema_path = "schemas/input/arena-schema-files.json"
    output_folder = "schemas/"

    with open(arena_objects_schema_path) as f:
        schema = json.load(f)

    with open(obj_schema_path) as f:
        obj_schema_file = json.load(f)

    definitions = schema["definitions"]
    arena_objects = schema["definitions"]["obj3d"]["oneOf"]

    component_definitions = {}
    for cobj_name in definitions:
        if cobj_name == "obj3d":
            continue
        component = True
        for obj in arena_objects:
            obj_name = obj["$ref"][len("#/definitions/") :]
            if obj_name == cobj_name:
                component = False
                break
        if component:
            component_definitions[cobj_name] = definitions[cobj_name]

    base_obj = {
        "definitions": component_definitions,
        "title": "",
        "description": "",
        "properties": schema["properties"],
        "required": schema["required"],
    }

    obj_schemas = {}
    for obj in arena_objects:
        obj_name = obj["$ref"][len("#/definitions/") :]
        new_obj = base_obj.copy()
        new_obj["properties"] = base_obj["properties"].copy()
        new_obj["title"] = obj["title"]
        new_obj["description"] = obj["description"]
        new_obj["properties"]["data"] = definitions[obj_name]
        new_obj["properties"]["data"]["title"] = f'{obj["title"]} Data'
        new_obj_json = json.dumps(new_obj, indent=4)
        file = open(os.path.join(output_folder, f"{obj_name}.json"), "w")
        file.write(new_obj_json)
        file.close()

        obj_schemas[obj_name] = {
            "file": f"schemas/{obj_name}.json",
            "title": obj["title"],
            "description": obj["description"],
        }

    obj_schemas.update(obj_schema_file)
    file = open(os.path.join(output_folder, "arena-schema-files.json"), "w")
    file.write(json.dumps(obj_schemas, indent=4))
    file.close()


# ---------------------------------------------------------------------------
# Docs (doc)
# ---------------------------------------------------------------------------

class Table:
    heading = ["Attribute", "Type", "Default", "Description", "Required"]
    cols = type("Columns", (object,), {"ATTR": 0, "TYPE": 1, "DFT": 2, "DESC": 3, "REQ": 4})()

def format_value_doc(obj, value):
    type = "object"
    if "type" in obj:
        type = obj["type"]
    if type == "string":
        return f"```'{value}'```"
    return f"```{value}```"

def write_md(json_obj, md_fn, object_name, output_folder, overwrite=True, wire_obj=True):
    if not overwrite:
        if os.path.isfile(md_fn):
            return
    print("->", md_fn)

    title = json_obj["title"]
    mdFile = MdUtils(file_name=md_fn, title=f"`{object_name}`")

    # include which type/attribute this is for
    if wire_obj:
        schema_desc = f"This is the schema for {title}, the properties of wire object type `{object_name}`."
    else:
        schema_desc = f"This is the schema for {title}, the properties of object `{object_name}`."

    desc = schema_desc
    if "description" in json_obj:
        desc = f"{json_obj['description']}\n\n{schema_desc}"
    mdFile.new_paragraph(desc)

    if wire_obj:
        mdFile.new_paragraph(
            "All wire objects have a set of basic attributes ```{object_id, action, type, persist, data}```. The ```data``` attribute defines the object-specific attributes"
        )

    mdFile.new_header(level=2, title=f"\n{title} Attributes", style="setext", add_table_of_contents="n")

    object_table(mdFile, title, json_obj, output_folder)

    if "example" in json_obj:
        mdFile.new_header(level=2, title=f"\n{title} Example", style="setext", add_table_of_contents="n")
        mdFile.insert_code(code=json.dumps(json_obj["example"], indent=4), language="json")

    if not "properties" in json_obj:
        mdFile.create_md_file()
        return

    if not "data" in json_obj["properties"]:
        mdFile.create_md_file()
        return

    mdFile.new_header(level=3, title=f"{title} Data Attributes", add_table_of_contents="n")

    if "$ref" in json_obj["properties"]["data"]:
        obj_name = json_obj["properties"]["data"]["$ref"][len("#/definitions/") :]
        object_table(mdFile, title, json_obj["definitions"][obj_name], output_folder, json_obj.get("definitions", {}))
    else:
        object_table(mdFile, title, json_obj["properties"]["data"], output_folder, json_obj.get("definitions", {}))

    mdFile.create_md_file()

def object_table(mdFile, md_title, obj, output_folder, definitions=None):
    if definitions is None:
        definitions = {}
    prop_list = {}
    if "properties" in obj:
        prop_list.update(obj["properties"])
    if "patternProperties" in obj:
        prop_list.update(obj["patternProperties"])
    if prop_list == {}:
        return
    required = []
    default = []
    if "definitions" in obj:
        definitions = obj["definitions"]
    if "required" in obj:
        required = obj["required"]
    if "default" in obj:
        default = obj["default"]
    table_lines = Table.heading.copy()
    for prop, prop_obj in prop_list.items():
        line = [""] * 5
        line[Table.cols.ATTR] = f"**{prop}**"
        line[Table.cols.REQ] = "No"
        if "type" in prop_obj:
            line[Table.cols.TYPE] = prop_obj["type"]
        if prop == "data":
            line[Table.cols.DESC] = f"{md_title} object data properties as defined below"
            line[Table.cols.REQ] = "Yes"
            line[Table.cols.TYPE] = f"{md_title} data"
        elif "default" in prop_obj:
            line[Table.cols.DFT] = format_value_doc(prop_obj, prop_obj["default"])
        if "description" in prop_obj:
            line[Table.cols.DESC] = prop_obj["description"].replace(" (derived from 'type' select above)", "")
        elif "title" in prop_obj:
            line[Table.cols.DESC] = prop_obj["title"]
        else:
            line[Table.cols.DESC] = prop
        if "enum" in prop_obj:
            if len(prop_obj["enum"]) == 1:
                type_val = prop_obj["enum"][0]
                if type_val in ObjTypeDesc:
                    line[Table.cols.DESC] = ObjTypeDesc[type_val]
                line[Table.cols.TYPE] = f"{line[Table.cols.TYPE]}; Must be: ```{type_val}```"
                line[Table.cols.DFT] = format_value_doc(prop_obj, type_val)
            else:
                line[Table.cols.TYPE] = f'{line[Table.cols.TYPE]}; One of: ```{prop_obj["enum"]}```'
        if prop in required:
            line[Table.cols.REQ] = "Yes"
        if prop in default:
            line[Table.cols.DFT] = format_value_doc(default, default[prop])
        if "$ref" in prop_obj:
            obj_name = prop_obj["$ref"][len("#/definitions/") :]
            if obj_name in definitions and "description" in definitions[obj_name]:
                line[Table.cols.DESC] = definitions[obj_name]["description"].split("\n")[0]
            line[Table.cols.TYPE] = f"[{obj_name}]({obj_name})"
            if obj_name in definitions:
                write_md(
                    definitions[obj_name],
                    os.path.join(output_folder, f"{obj_name}.md"),
                    obj_name,
                    output_folder,
                    overwrite=False,
                    wire_obj=False,
                )
        if "deprecated" in prop_obj:
            for col in range(Table.cols.REQ + 1):
                if line[col]:
                    line[col] = f"~~{line[col]}~~"

        elif "type" in prop_obj and prop_obj["type"] == "object":
            if "properties" in obj:
                write_md(
                    obj["properties"][prop],
                    os.path.join(output_folder, f"{prop}.md"),
                    prop,
                    output_folder,
                    overwrite=True,
                    wire_obj=False,
                )

        table_lines.extend(line)

    mdFile.new_table(
        columns=len(Table.heading), rows=len(table_lines) // len(Table.heading), text=table_lines, text_align="left"
    )

def cmd_doc(args):
    input_folder = "schemas"
    output_folder = "docs"

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    dir_enc = os.fsencode(input_folder)
    for file in os.listdir(dir_enc):
        filename = os.fsdecode(file)
        if filename.endswith(".json") and not filename.startswith("arena-schema-files"):
            json_filename = os.path.join(input_folder, filename)
            filename_noext = os.fsdecode(os.path.splitext(file)[0])
            md_filename = os.path.join(output_folder, f"{filename_noext}.md")
            with open(json_filename) as f:
                json_obj = json.load(f)
            prefix_removed = filename_noext
            if prefix_removed.startswith("arena-"):
                prefix_removed = prefix_removed[6:]
            write_md(json_obj, md_filename, prefix_removed, output_folder)


# ---------------------------------------------------------------------------
# Jekyll (jekyll)
# ---------------------------------------------------------------------------

def cmd_jekyll(args):
    input_folder = "docs"
    obj_schema_path = "schemas/arena-schema-files.json"
    output_folder = args.dst

    if not os.path.isdir(output_folder):
        os.mkdir(output_folder)

    for oldpath in glob.iglob(os.path.join(output_folder, "*.md")):
        os.remove(oldpath)

    sec_title = "ARENA Objects"
    sec_sub_title = "Objects Schema"

    md_lines = []
    md_lines.append("---\n")
    md_lines.append(f"title: {sec_sub_title}\n")
    md_lines.append("layout: default\n")
    md_lines.append(f"parent: {sec_title}\n")
    md_lines.append("has_children: true\n")
    md_lines.append("has_toc: false\n")
    md_lines.append("---\n")
    md_lines.append("\n<!--CAUTION: This file is autogenerated from https://github.com/arenaxr/arena-schemas. Changes made here may be overwritten.-->\n\n")
    md_lines.append("# ARENA Message Objects\n\n")
    md_lines.append("|Object Message|Description|\n")
    md_lines.append("| :--- | :--- |\n")

    if os.path.exists(obj_schema_path):
        with open(obj_schema_path, "r") as json_file_all:
            files = json.load(json_file_all)
        for file in files:
            filename = os.path.basename(files[file]["file"])
            title = files[file]["title"]
            desc = files[file]["description"]
            md_lines.append(f"|[{title}]({filename[:-5]})|{desc}|\n")
    else:
        print(f"Warning: {obj_schema_path} missing.")

    out = "".join(md_lines)
    index_path = os.path.join(output_folder, "index.md")
    print(f"->{index_path}")
    with open(index_path, "w") as f:
        f.write(out)

    for filename in sorted(os.listdir(input_folder)):
        with open(os.path.join(input_folder, filename), "r") as f:
            text = f.read()
        lines = text.split("\n")
        title_val = lines[1].strip("`")
        md_lines = []
        md_lines.append("---\n")
        md_lines.append(f"title: {title_val}\n")
        md_lines.append("layout: default\n")
        md_lines.append(f"parent: {sec_sub_title}\n")
        md_lines.append(f"grand_parent: {sec_title}\n")
        md_lines.append("---\n")
        md_lines.append("\n<!--CAUTION: This file is autogenerated from https://github.com/arenaxr/arena-schemas. Changes made here may be overwritten.-->\n\n")
        md_lines.append(text)
        out = "".join(md_lines)
        md_path = os.path.join(output_folder, filename)
        print(f"->{md_path}")
        with open(md_path, "w") as f:
            f.write(out)


# ---------------------------------------------------------------------------
# Python (py)
# ---------------------------------------------------------------------------

def definition_py(name, prop):
    title = get_prop(prop, "title")
    description = get_prop(prop, "description")
    deprecated = get_prop(prop, "deprecated")
    define = None
    if description:
        define = description
    elif title:
        define = title
    else:
        define = name
    if deprecated:
        define = f"*{define}*"  # add italics
    return (
        define.replace("\n", " ")
        .replace("\\", "\\\\")
        .replace("  ", " ")
        .replace("<a href='", "<")
        .replace("'>", "> ")
        .replace("</a>", "")
        .replace("deprecated", "**deprecated**")
        .replace("DEPRECATED", "**DEPRECATED**")
    )

def jstype2pytype(jstype, arraytype):
    if jstype == "null":
        return "None"
    elif jstype == "number":
        return "float"
    elif jstype == "integer":
        return "int"
    elif jstype == "boolean":
        return "bool"
    elif jstype == "string":
        return "str"
    elif jstype == "array":
        if arraytype is not None:
            return f"list[{jstype2pytype(arraytype, None)}]"
        else:
            return "list"
    elif jstype == "object":
        return "dict"
    else:
        return "dict"

def jsenum2str(prop):
    if "enum" in prop:
        s = ", "
        items = s.join(prop["enum"])
        return f" Allows [{items}]"
    return ""

def write_py_class(prop_schema, prop_name, tag_name, output_folder, attr_classes, obj_classes):
    AltUsages = {
        "click-listener": ["clickable=True"],
        "color": ["color=Color(red,green,blue)", "color=(red,green,blue)"],
        "position": ["position=Position(x,y,z)", "position=(x,y,z)"],
        "rotation": ["rotation=Rotation(x,y,z,w)", "rotation=Rotation(x,y,z)", "rotation=(x,y,z,w)", "rotation=(x,y,z)"],
        "scale": ["scale=Scale(x,y,z)", "scale=(x,y,z)"],
    }
    FirstIterable = ["color", "position", "rotation", "scale"]

    if "properties" in prop_schema:
        prop_schema["properties"] = collections.OrderedDict(sorted(prop_schema["properties"].items()))
    prop_class = pascalcase(prop_name)
    prop_ns = snakecase(prop_name)
    prop_dict = prop_name.replace("-", "_")
    uses = [f"`{prop_dict}={prop_class}(...)`"]  # default usage
    if prop_name in AltUsages:
        for use in AltUsages[prop_name]:
            uses.append(f"`{use}`")
    prop_usage = " or ".join(uses)
    iterable = None
    if prop_name in FirstIterable:
        iterable = "|Iterable|Mapping"
    if tag_name == "objects":
        obj_classes[prop_ns] = prop_class
    py_path = os.path.join(output_folder, tag_name, f"{prop_ns}.py")

    # add object class if needed
    if not os.path.isfile(py_path):
        with open(f"templates/py_{tag_name}_class.j2") as tfile:
            t = jinja2.Template(tfile.read())
        class_out = t.render(
            prop_schema=prop_schema,
            prop_dict=prop_dict,
            prop_class=prop_class,
            prop_name=prop_name,
            definition=definition_py,
        )
        print(f"->{py_path}")
        pfile = open(py_path, "w")
        pfile.write(f"{class_out}\n")
        pfile.close()

    # update the object docstring only
    pfile = open(py_path, "r")
    lines = pfile.readlines()
    pfile.close()
    with open(f"templates/py_{tag_name}_docstring.j2") as tfile:
        t = jinja2.Template(tfile.read())
        t.globals["jstype2pytype"] = jstype2pytype
        t.globals["jsenum2str"] = jsenum2str
    docstr_out = t.render(
        prop_schema=prop_schema,
        prop_dict=prop_dict,
        prop_class=prop_class,
        prop_name=prop_name,
        prop_usage=prop_usage,
        definition=definition_py,
        iterable=iterable,
    )
    class_dec = f"class {prop_class}("
    print(f"->{py_path}")
    pfile = open(py_path, "w")
    found_class = False
    found_doc = False
    for line in lines:
        if line.startswith(class_dec):
            found_class = True
            pfile.write(line)
        elif found_class and '"""' in line:
            found_class = False
            found_doc = True
            pfile.write(f"{docstr_out}\n")
        elif found_doc:
            if '"""' in line:
                found_doc = False
        else:
            pfile.write(line)
    pfile.close()

def generate_intermediate_json_py(list_fns, input_folder, output_folder):
    obj_schemas = {}
    obj_classes = {}
    attr_classes = {}
    attr_schema = {}

    for list_fn in list_fns:
        obj_schema_path = os.path.join(input_folder, list_fn)
        with open(obj_schema_path) as tfile:
            obj_schemas.update(json.load(tfile))
        for _, obj_schema in obj_schemas.items():
            fn = obj_schema["file"]
            with open(os.path.join(input_folder, fn)) as tfile:
                schema = json.load(tfile)

            # resolve references
            if "allOf" in schema:
                new_schema = parse_allof_ref(schema, input_folder, attr_classes=attr_classes, obj_attr_schema=attr_schema)
                del schema["allOf"]
            else:
                new_schema = schema
            if "allOf" in new_schema["properties"]["data"]:
                new_schema["properties"]["data"] = parse_allof_ref(new_schema["properties"]["data"], input_folder, False, attr_classes=attr_classes, obj_attr_schema=attr_schema)
                del new_schema["properties"]["data"]["allOf"]

            # generate definitions
            if "definitions" not in new_schema:
                new_schema["definitions"] = {}
            if "data" in new_schema["properties"] and "properties" in new_schema["properties"]["data"]:
                dprops = new_schema["properties"]["data"]["properties"]
                for key in dprops:
                    if "type" in dprops[key] and dprops[key]["type"] == "object" and "deprecated" not in dprops[key]:
                        if key not in new_schema["definitions"]:
                            new_schema["definitions"][key] = dprops[key]
                            new_schema["properties"]["data"]["properties"][key] = {"$ref": f"#/definitions/{key}"}

            # write this object expanded json schema
            if "properties" not in new_schema["properties"]["data"]:
                continue
            if "object_type" not in new_schema["properties"]["data"]["properties"]:
                continue

            # export object classes
            for object_type in new_schema["properties"]["data"]["properties"]["object_type"]["enum"]:
                new_schema["properties"]["data"]["description"] = new_schema["description"]
                write_py_class(new_schema["properties"]["data"], object_type, "objects", output_folder, attr_classes, obj_classes)

        # export attribute classes
        for prop in attr_schema:
            if "type" in attr_schema[prop] and attr_schema[prop]["type"] == "object":
                write_py_class(attr_schema[prop], prop, "attributes", output_folder, attr_classes, obj_classes)

        data_schema = {}
        data_schema["description"] = "Wraps all attributes in JSON."
        data_schema["properties"] = collections.OrderedDict(sorted(attr_schema.items()))

        # export data class
        write_py_class(data_schema, "data", "attributes", output_folder, attr_classes, obj_classes)

        # export attribute translation map
        with open("templates/py_attributes_translate.j2") as tfile:
            t = jinja2.Template(tfile.read())
        py_path = os.path.join(output_folder, "attributes", "translate.py")
        print(f"->{py_path}")
        pfile = open(py_path, "w")
        init_out = t.render(prop_schema=data_schema, snakecase=snakecase, pascalcase=pascalcase)
        pfile.write(f"{init_out}\n")
        pfile.close()

        # export objects init file
        obj_classes = collections.OrderedDict(sorted(obj_classes.items()))
        with open("templates/py_objects_init.j2") as tfile:
            t = jinja2.Template(tfile.read())
        py_path = os.path.join(output_folder, "objects", "__init__.py")
        print(f"->{py_path}")
        pfile = open(py_path, "w")
        init_out = t.render(classes=obj_classes)
        pfile.write(f"{init_out}\n")
        pfile.close()

        # export attributes init file
        attr_classes = collections.OrderedDict(sorted(attr_classes.items()))
        with open("templates/py_attributes_init.j2") as tfile:
            t = jinja2.Template(tfile.read())
        py_path = os.path.join(output_folder, "attributes", "__init__.py")
        print(f"->{py_path}")
        pfile = open(py_path, "w")
        init_out = t.render(classes=attr_classes)
        pfile.write(f"{init_out}\n")
        pfile.close()


def cmd_py(args):
    if not os.path.isdir(args.src):
        print("Supply a valid source schemas path! src=arena-web-core/build")
        return
    if not os.path.isdir(args.dst):
        print("Supply a valid destination schemas path! dst=arena-py/arena")
        return

    input_folder = args.src
    output_folder = args.dst

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    generate_intermediate_json_py(["schemas/arena-schema-files.json", "schemas/arena-schema-files-nonpersist.json"], input_folder, output_folder)


# ---------------------------------------------------------------------------
# Dotnet (dotnet)
# ---------------------------------------------------------------------------

def enumcase(word):
    if word and word[0:1].isdigit():
        # convert if first char is a number, which is an illegal enum name in cs
        sub_words = re.split(r"(\d+)", word)
        num2worded = "-".join(list(map(lambda x: wordify(x), sub_words)))
        return pascalcase(num2worded)
    else:
        return pascalcase(word)

def wordify(txt):
    if txt.isnumeric():
        return num2words.num2words(txt)
    return txt

def jstype2cstype(prop):
    jstype = get_prop(prop, "type")
    ref = get_prop(prop, "$ref")
    default = get_prop(prop, "default")
    nulldec = ""
    if default is None:
        nulldec = "?"
    if jstype == "number":
        return f"float{nulldec}"
    elif jstype == "integer":
        return f"int{nulldec}"
    elif jstype == "boolean":
        return f"bool{nulldec}"
    elif jstype == "string":
        return "string"
    elif jstype == "array":
        return f'{jstype2cstype(get_prop(prop, "items"))}[]'
    else:
        if ref:
            ref_name = pascalcase(ref.split("/")[-1])
            return f"Arena{ref_name}Json"
        else:
            return "object"

def format_value_cs(prop):
    jstype = get_prop(prop, "type")
    ref = get_prop(prop, "$ref")
    default = get_prop(prop, "default")
    items = get_prop(prop, "items")
    if default is None:
        return "null"
    if jstype == "string":
        return f'"{str(default)}"'
    elif jstype == "boolean":
        return f"{str(default).lower()}"
    elif jstype == "number":
        return f"{float(default):g}f"
    elif jstype == "integer":
        return f"{int(default)}"
    elif jstype == "array":
        array = []
        items_type = get_prop(items, "type")
        for item in default:
            if items_type == "object":
                array.append(format_value_cs({"type": items_type, "default": str(json.dumps(item))}))
            else:
                array.append(format_value_cs({"type": items_type, "default": str(item)}))
        return f'{{ {", ".join(array)} }}'
    else:
        default_json = str(default).replace('"', "'")
        if ref:
            ref_name = pascalcase(ref.split("/")[-1])
            return f'JsonConvert.DeserializeObject<Arena{ref_name}Json>("{default_json}")'
        else:
            return f'JsonConvert.DeserializeObject("{default_json}")'

def write_cs_class(prop_schema, prop_name, tag_name, output_folder, obj_classes, log_todos=False):
    prop_class = f"Arena{pascalcase(prop_name)}Json"
    prop_ns = snakecase(prop_name)
    if tag_name == "objects":
        obj_classes[prop_ns] = prop_class
    cs_path = os.path.join(output_folder, f"{prop_class}.cs")

    # add object class
    with open(f"templates/cs_{tag_name}_class.j2") as tfile:
        t = jinja2.Template(tfile.read())
    class_out = t.render(
        prop_schema=prop_schema,
        prop_class=prop_class,
        prop_name=prop_name,
        pascalcase=pascalcase,
        enumcase=enumcase,
        jstype2cstype=jstype2cstype,
        format_value=format_value_cs,
        definition=definition_py_cs,
    )
    print(f"->{cs_path}")
    pfile = open(cs_path, "w")
    pfile.write(f"{class_out}\n")
    pfile.close()

    if log_todos and "properties" in prop_schema:
        print(f"        // ARENA {prop_name} component unity conversion status:")
        for propname, prop in prop_schema["properties"].items():
            if propname != "object_type":
                print(f"        // TODO: {propname}")

def generate_intermediate_json_cs(list_fns, input_folder, output_folder):
    obj_schemas = {}
    obj_classes = {}
    attr_classes = {}
    obj_attr_schema = {}

    for list_fn in list_fns:
        obj_schema_path = os.path.join(input_folder, list_fn)
        with open(obj_schema_path) as tfile:
            obj_schemas.update(json.load(tfile))
        for _, obj_schema in obj_schemas.items():
            fn = obj_schema["file"]
            with open(os.path.join(input_folder, fn)) as tfile:
                schema = json.load(tfile)

            # resolve references
            if "allOf" in schema:
                new_schema = parse_allof_ref(schema, input_folder, attr_classes=attr_classes, obj_attr_schema=obj_attr_schema)
                del schema["allOf"]
            else:
                new_schema = schema
            if "allOf" in new_schema["properties"]["data"]:
                new_schema["properties"]["data"] = parse_allof_ref(new_schema["properties"]["data"], input_folder, False, attr_classes=attr_classes, obj_attr_schema=obj_attr_schema)
                del new_schema["properties"]["data"]["allOf"]
            if "$ref" in new_schema["properties"]["data"]:
                key = new_schema["properties"]["data"]["$ref"].split("/")[-1]
                new_schema["properties"]["data"] = new_schema["definitions"][key]

            # generate definitions
            if "definitions" not in new_schema:
                new_schema["definitions"] = {}
            if "data" in new_schema["properties"] and "properties" in new_schema["properties"]["data"]:
                dprops = new_schema["properties"]["data"]["properties"]
                for key in dprops:
                    if "type" in dprops[key] and dprops[key]["type"] == "object" and "deprecated" not in dprops[key]:
                        if key not in new_schema["definitions"]:
                            new_schema["definitions"][key] = dprops[key]
                            new_schema["properties"]["data"]["properties"][key] = {"$ref": f"#/definitions/{key}"}

            if "properties" not in new_schema["properties"]["data"]:
                continue

            new_schema["properties"]["data"]["description"] = definition_py_cs(new_schema["properties"]["type"], new_schema)
            if "object_type" in new_schema["properties"]["data"]["properties"]:
                for object_type in new_schema["properties"]["data"]["properties"]["object_type"]["enum"]:
                    write_cs_class(new_schema["properties"]["data"], object_type, "objects", output_folder, obj_classes)
            else:
                prop_name = os.path.splitext(os.path.basename(fn))[0]
                write_cs_class(new_schema["properties"]["data"], prop_name, "attributes", output_folder, obj_classes)
                for prop in new_schema["properties"]["data"]["properties"]:
                    if "$ref" in new_schema["properties"]["data"]["properties"][prop]:
                        key = new_schema["properties"]["data"]["properties"][prop]["$ref"].split("/")[-1]
                        write_cs_class(new_schema["definitions"][key], key, "attributes", output_folder, obj_classes)

        for prop in obj_attr_schema:
            if "type" in obj_attr_schema[prop] and obj_attr_schema[prop]["type"] in ObjTypeDesc:
                write_cs_class(obj_attr_schema[prop], prop, "attributes", output_folder, obj_classes)

        data_schema = {}
        data_schema["description"] = "Wraps all attributes in JSON."
        data_schema["properties"] = obj_attr_schema

        write_cs_class(data_schema, "data", "attributes", output_folder, obj_classes)


def cmd_dotnet(args):
    if not os.path.isdir(args.src):
        print("Supply a valid source schemas path! src=arena-web-core/build")
        return
    if not os.path.isdir(args.dst):
        print("Supply a valid destination schemas path! dst=arena-unity/Runtime/Schemas")
        return

    input_folder = args.src
    output_folder = args.dst

    # clean dest
    for oldpath in glob.iglob(os.path.join(output_folder, "*.cs")):
        os.remove(oldpath)

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    generate_intermediate_json_cs(["schemas/arena-schema-files.json", "schemas/arena-schema-files-nonpersist.json"], input_folder, output_folder)


# ---------------------------------------------------------------------------
# CLI Argument Parsing
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="ARENA Schema Builder")
    subparsers = parser.add_subparsers(dest="command", help="commands", required=True)

    parser_main = subparsers.add_parser("main", help="Run main schema builder logic")
    parser_main.set_defaults(func=cmd_main)

    parser_update = subparsers.add_parser("update", help="Update intermediate schemas")
    parser_update.add_argument("src", help="Source folder of schemas (e.g. from arena-web-core/build)")
    parser_update.set_defaults(func=cmd_update)

    parser_doc = subparsers.add_parser("doc", help="Generate Markdown documentation")
    parser_doc.set_defaults(func=cmd_doc)

    parser_jekyll = subparsers.add_parser("jekyll", help="Generate Jekyll site files")
    parser_jekyll.add_argument("dst", help="Destination folder for Jekyll markdown")
    parser_jekyll.set_defaults(func=cmd_jekyll)

    parser_py = subparsers.add_parser("py", help="Generate Python classes")
    parser_py.add_argument("src", help="Source folder of schemas (e.g. from arena-web-core/build)")
    parser_py.add_argument("dst", help="Destination folder for Python code")
    parser_py.set_defaults(func=cmd_py)

    parser_dotnet = subparsers.add_parser("dotnet", help="Generate C#/.NET classes")
    parser_dotnet.add_argument("src", help="Source folder of schemas (e.g. from arena-web-core/build)")
    parser_dotnet.add_argument("dst", help="Destination folder for C# code")
    parser_dotnet.set_defaults(func=cmd_dotnet)

    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()
