import glob
import json
import os
import re
import sys

import jinja2
import num2words
from caseconverter import pascalcase, snakecase

output_folder = ""
input_folder = ""
obj_attr_schema = {}
log_todos = False

ObjTypeDesc = {
    "object": "AFrame 3D Object",
    "program": "ARENA program data",
    "scene-options": "ARENA scene options",
    "landmarks": "ARENA landmarks",
    "camera-override": "ARENA camera override data",
}


def get_prop(prop, key):
    if key in prop:
        return prop[key]
    else:
        return None


def definition(name, prop):
    title = get_prop(prop, "title")
    description = get_prop(prop, "description")
    if description:
        return description.replace("\n", " ").replace("  ", " ")
    elif title:
        return title
    else:
        return name


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
    # print(f'{jstype}, {ref}, {default}')
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
    else:  # jstype == 'object' or  jstype == 'null':
        if ref:
            ref_name = pascalcase(ref.split("/")[-1])
            return f"Arena{ref_name}Json"
        else:
            return "object"


def format_value(prop):
    jstype = get_prop(prop, "type")
    ref = get_prop(prop, "$ref")
    default = get_prop(prop, "default")
    items = get_prop(prop, "items")
    # print(f'{jstype}, {ref}, {default}, {items}')
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
                array.append(format_value({"type": items_type, "default": str(json.dumps(item))}))
            else:
                array.append(format_value({"type": items_type, "default": str(item)}))
        return f'{{ {", ".join(array)} }}'
    else:  # type == 'object':
        default_json = str(default).replace('"', "'")
        if ref:
            ref_name = pascalcase(ref.split("/")[-1])
            return f'JsonConvert.DeserializeObject<Arena{ref_name}Json>("{default_json}")'
        else:
            return f'JsonConvert.DeserializeObject("{default_json}")'


def parse_allof_ref(allof_schema, expand_refs=True):
    global input_folder, attr_classes, obj_attr_schema
    new_schema = allof_schema
    for props in allof_schema["allOf"]:
        for key in props:
            if key == "$ref":
                ref = props[key].split("#/")
                key = ref[1]
                with open(os.path.join(input_folder, ref[0])) as f:
                    sub_schema = json.load(f)
                if expand_refs:
                    props = sub_schema
                else:
                    for prop in sub_schema["properties"]:
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


def main():
    global input_folder, output_folder
    args = sys.argv[1:]
    print(args)
    if len(args) == 0 or not os.path.isdir(args[0]):
        print("Supply a valid source schemas path! src=arena-web-core/build")
        return
    input_folder = args[0]

    if len(args) == 0 or not os.path.isdir(args[0]):
        print("Supply a valid destination schemas path! dst=arena-unity/Runtime/Schemas")
        return
    output_folder = args[1]

    # clean dest
    for oldpath in glob.iglob(os.path.join(output_folder, "*.cs")):
        os.remove(oldpath)

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    generate_intermediate_json(["schemas/arena-schema-files.json", "schemas/arena-schema-files-nonpersist.json"])


def generate_intermediate_json(list_fns):
    global input_folder, output_folder, obj_classes, attr_classes
    obj_schemas = {}
    obj_classes = {}
    attr_classes = {}
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
                new_schema = parse_allof_ref(schema)
                del schema["allOf"]
            else:
                new_schema = schema
            if "allOf" in new_schema["properties"]["data"]:
                new_schema["properties"]["data"] = parse_allof_ref(new_schema["properties"]["data"], False)
                del new_schema["properties"]["data"]["allOf"]
            if "$ref" in new_schema["properties"]["data"]:
                key = new_schema["properties"]["data"]["$ref"].split("/")[-1]
                new_schema["properties"]["data"] = new_schema["definitions"][key]
            # if 'deprecated' in new_schema and new_schema['deprecated']:
            #     continue

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

            new_schema["properties"]["data"]["description"] = definition(new_schema["properties"]["type"], new_schema)
            if "object_type" in new_schema["properties"]["data"]["properties"]:
                # export object classes
                for object_type in new_schema["properties"]["data"]["properties"]["object_type"]["enum"]:
                    write_cs_class(new_schema["properties"]["data"], object_type, "objects")
            else:
                # export non-object high level classes
                prop_name = os.path.splitext(os.path.basename(fn))[0]
                write_cs_class(new_schema["properties"]["data"], prop_name, "attributes")
                for prop in new_schema["properties"]["data"]["properties"]:
                    if "$ref" in new_schema["properties"]["data"]["properties"][prop]:
                        # export non-object attribute classes
                        key = new_schema["properties"]["data"]["properties"][prop]["$ref"].split("/")[-1]
                        write_cs_class(new_schema["definitions"][key], key, "attributes")

        # export attribute classes
        for prop in obj_attr_schema:
            if "type" in obj_attr_schema[prop] and obj_attr_schema[prop]["type"] in ObjTypeDesc:
                write_cs_class(obj_attr_schema[prop], prop, "attributes")

        data_schema = {}
        data_schema["description"] = "Wraps all attributes in JSON."
        data_schema["properties"] = obj_attr_schema
        # data_schema['properties'] = collections.OrderedDict(
        #     sorted(data_schema['properties'].items()))

        # export data class
        write_cs_class(data_schema, "data", "attributes")
        # os.rename(os.path.join(output_folder, 'ArenaObjectDataJson.cs'),
        #           os.path.join(output_folder, '../ArenaObjectDataJson.cs'))


def write_cs_class(prop_schema, prop_name, tag_name):
    # if 'properties' in prop_schema:
    #     prop_schema['properties'] = collections.OrderedDict(
    #         sorted(prop_schema['properties'].items()))
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
        format_value=format_value,
        definition=definition,
    )
    print(f"->{cs_path}")
    pfile = open(cs_path, "w")
    pfile.write(f"{class_out}\n")
    pfile.close()

    # log optional attribute TODOs
    if log_todos and "properties" in prop_schema:
        print(f"        // ARENA {prop_name} component unity conversion status:")
        for propname, prop in prop_schema["properties"].items():
            if propname != "object_type":
                print(f"        // TODO: {propname}")


if __name__ == "__main__":
    main()
