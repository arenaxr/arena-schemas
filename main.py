import json
import os

arena_objects_schema_path = "schemas/input/arena-obj3d.json"
obj_schema_path = "schemas/input/arena-schema-files.json"
output_folder = "schemas/"


def main():
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
        new_obj = base_obj
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


"""
    for key in definitions:
            print(key, '->', definitions[key])
            break

    file1 = open("myfile.txt","w")
"""

if __name__ == "__main__":
    main()
