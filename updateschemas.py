import json
import os
import sys

output_folder = 'schemas/'
input_folder = ''


def parse_allof_ref(allof_schema):
    global input_folder
    new_schema = allof_schema
    for props in allof_schema['allOf']:
        for key in props:
            if key == '$ref':
                ref = props[key].split('#/')
                key = ref[1]
                with open(f'{input_folder}/{ref[0]}') as f:
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
    if (len(args) == 0 or not os.path.isdir(args[0])):
        print('Supply a valid source schemas path! src=ARENA-core/build')
        return

    input_folder = args[0]
    obj_schema_path = f'{input_folder}/schemas/arena-schema-files.json'

    with open(obj_schema_path) as f:
        obj_schemas = json.load(f)
    for obj_schema in obj_schemas:
        fn = obj_schemas[obj_schema]['file']
        with open(f'{input_folder}/{fn}') as f:
            schema = json.load(f)

        # resolve all references
        if 'allOf' in schema:
            new_schema = parse_allof_ref(schema)
            del schema['allOf']
        else:
            new_schema = schema

        if 'allOf' in new_schema['properties']['data']:
            new_schema['properties']['data'] = parse_allof_ref(new_schema['properties']['data'])
            del new_schema['properties']['data']['allOf']
        else:
            new_schema['properties']['data'] = new_schema['properties']['data']

        # resolve missing definitions

        # write this object expanded json schema
        new_obj_json = json.dumps(new_schema, indent=4)
        file = open(f'{output_folder}{fn[8:]}', 'w')
        file.write(new_obj_json)
        file.close()

        break # for now

    file = open(f'{output_folder}arena-schema-files.json', 'w')
    file.write(json.dumps(obj_schemas, indent=4))
    file.close()

    # with open(arena_objects_schema_path) as f:
    #     schema = json.load(f)

    # with open(obj_schema_path) as f:
    #     obj_schema_file = json.load(f)

    # definitions = schema['definitions']
    # arena_objects = schema['definitions']['obj3d']['oneOf']

    # component_definitions = {}
    # for cobj_name in definitions:
    #     if (cobj_name == 'obj3d'): continue
    #     component = True
    #     for obj in arena_objects:
    #         obj_name = obj['$ref'][len('#/definitions/'):]
    #         if (obj_name == cobj_name):
    #             component = False
    #             break
    #     if (component):
    #         component_definitions[cobj_name] = definitions[cobj_name]

    # base_obj = {
    #     'definitions': component_definitions,
    #     'title': '',
    #     'description': '',
    #     'properties': schema['properties'],
    #     'required': schema['required']
    # }

    # obj_schemas = {}
    # for obj in arena_objects:
    #     obj_name = obj['$ref'][len('#/definitions/'):]
    #     new_obj = base_obj
    #     new_obj['title'] = obj['title']
    #     new_obj['description'] = obj['description']
    #     new_obj['properties']['data'] = definitions[obj_name]
    #     new_obj['properties']['data']['title'] = f"{obj['title']} Data"
    #     new_obj_json = json.dumps(new_obj, indent=4)
    #     file = open(f'{output_folder}{obj_name}.json','w')
    #     file.write(new_obj_json)
    #     file.close()

    #     obj_schemas[obj_name]={
    #         'file': f'schemas/{obj_name}.json',
    #         'title': obj['title'],
    #         'description': obj['description'],
    #     }

    # obj_schemas.update(obj_schema_file)
    # file = open(f'{output_folder}arena-schema-files.json','w')
    # file.write(json.dumps(obj_schemas, indent=4))
    # file.close()


'''
    for key in definitions:
            print(key, '->', definitions[key])
            break

    file1 = open('myfile.txt','w')
'''

if __name__ == '__main__':
    main()
