import json
import os
import sys

from caseconverter import pascalcase, snakecase
from jinja2 import Template

output_folder = ''
input_folder = ''


def parse_allof_ref(allof_schema):
    global input_folder
    new_schema = allof_schema
    for props in allof_schema['allOf']:
        for key in props:
            if key == '$ref':
                ref = props[key].split('#/')
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
    if (len(args) == 0 or not os.path.isdir(args[0])):
        print('Supply a valid source schemas path! src=arena-web-core/build')
        return
    input_folder = args[0]

    if (len(args) == 0 or not os.path.isdir(args[0])):
        print('Supply a valid destination  schemas path! dst=arena-py/arena')
        return
    output_folder = args[1]

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    generate_intermediate_json(
        ['schemas/arena-schema-files.json', 'schemas/arena-schema-files-nonpersist.json'])


def generate_intermediate_json(list_fns):
    global input_folder, output_folder
    obj_schemas = {}
    for list_fn in list_fns:
        obj_schema_path = os.path.join(input_folder, list_fn)
        with open(obj_schema_path) as tfile:
            obj_schemas.update(json.load(tfile))
        for _, obj_schema in obj_schemas.items():
            fn = obj_schema['file']
            with open(os.path.join(input_folder, fn)) as tfile:
                schema = json.load(tfile)

            # resolve references
            if 'allOf' in schema:
                new_schema = parse_allof_ref(schema)
                del schema['allOf']
            else:
                new_schema = schema
            if 'allOf' in new_schema['properties']['data']:
                new_schema['properties']['data'] = parse_allof_ref(
                    new_schema['properties']['data'])
                del new_schema['properties']['data']['allOf']

            # generate definitions
            if 'definitions' not in new_schema:
                new_schema['definitions'] = {}
            if 'data' in new_schema['properties'] and 'properties' in new_schema['properties']['data']:
                dprops = new_schema['properties']['data']['properties']
                for key in dprops:
                    if 'type' in dprops[key] and dprops[key]['type'] == 'object':
                        if key not in new_schema['definitions']:
                            new_schema['definitions'][key] = dprops[key]
                            new_schema['properties']['data']['properties'][key] = {
                                '$ref': f'#/definitions/{key}'}

            # write this object expanded json schema
            with open('templates/py_object_class.j2') as tfile:
                t = Template(tfile.read())
            obj_type = new_schema['properties']['data']['properties']['object_type']['enum'][0]
            obj_class = pascalcase(obj_type)
            obj_fname = f'{snakecase(obj_type)}.py'
            pfile = open(os.path.join(output_folder, obj_fname), 'w')
            str_out = t.render(obj_schema=new_schema,
                               obj_class=obj_class,
                               obj_type=obj_type)
            pfile.write(f'{str_out}\n')
            pfile.close()


if __name__ == '__main__':
    main()
