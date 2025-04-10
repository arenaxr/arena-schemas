import json
import os
import sys

output_folder = "schemas"
input_folder = ""

def parse_allof_ref(allof_schema):
    global input_folder
    new_schema = allof_schema
    for props in allof_schema["allOf"]:
        for key in props:
            if key == "$ref":
                ref = props[key].split("#/")
                key = ref[1]
                with open(os.path.join(input_folder, ref[0])) as f:
                    sub_schema = json.load(f)
                props = sub_schema
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
    generate_intermediate_json(["schemas/arena-schema-files.json", "schemas/arena-schema-files-nonpersist.json"])


def generate_intermediate_json(list_fns):
    global input_folder, output_folder
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
                new_schema = parse_allof_ref(schema)
                del schema["allOf"]
            else:
                new_schema = schema
            if "allOf" in new_schema["properties"]["data"]:
                new_schema["properties"]["data"] = parse_allof_ref(new_schema["properties"]["data"])
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


if __name__ == "__main__":
    main()
