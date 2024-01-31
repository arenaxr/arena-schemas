import collections
import json
import os
import sys

from caseconverter import pascalcase, snakecase, camelcase
from jinja2 import Template

output_folder = ''
input_folder = ''
attr_schema = {}


def jstype2cstype(jstype, arraytype):
    if jstype == "null":
        return "null"
    elif jstype == "number":
        return "float"
    elif jstype == "integer":
        return "int"
    elif jstype == "boolean":
        return "bool"
    elif jstype == "string":
        return "string"
    elif jstype == "array":
        if arraytype is not None:
            return f"{{{jstype2cstype(arraytype, None)}}}"
        else:
            return "{{}}"
    elif jstype == "object":
        return "object"
    else:
        return "object"


def format_value(type, value):
    if type == 'string':
        return f'\"{value}\"'
    elif type == 'boolean':
        return f'{str(value).lower()}'
    elif type == 'number':
        return f'{"{0:g}".format(float(value))}f'
    elif type == 'integer':
        return f'{int(value)}'
    elif type == 'array':
        format_array = str(value).replace(
            "[", "{").replace("]", "}").replace("'", "\"")
        return f'{format_array}'
    return f'{value}'


def jsenum2str(prop):
    if 'enum' in prop:
        s = ', '
        items = s.join(prop['enum'])
        return f' Allows [{items}]'
    return ''


def parse_allof_ref(allof_schema, expand_refs=True):
    global input_folder, attr_classes, attr_schema
    new_schema = allof_schema
    for props in allof_schema['allOf']:
        for key in props:
            if key == '$ref':
                ref = props[key].split('#/')
                key = ref[1]
                with open(os.path.join(input_folder, ref[0])) as f:
                    sub_schema = json.load(f)
                if expand_refs:
                    props = sub_schema
                else:
                    for prop in sub_schema['properties']:
                        attr_class = pascalcase(prop)
                        attr_ns = snakecase(prop)
                        attr_schema[prop] = sub_schema['properties'][prop]
                        if 'properties' in sub_schema['properties'][prop]:
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
    if (len(args) == 0 or not os.path.isdir(args[0])):
        print('Supply a valid source schemas path! src=arena-web-core/build')
        return
    input_folder = args[0]

    if (len(args) == 0 or not os.path.isdir(args[0])):
        print('Supply a valid destination  schemas path! dst=arena-cs/arena')
        return
    output_folder = args[1]

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    generate_intermediate_json(
        ['schemas/arena-schema-files.json', 'schemas/arena-schema-files-nonpersist.json'])


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
                    new_schema['properties']['data'], False)
                del new_schema['properties']['data']['allOf']
            if 'deprecated' in new_schema and new_schema['deprecated']:
                continue

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
            if 'properties' not in new_schema['properties']['data']:
                continue
            if 'object_type' not in new_schema['properties']['data']['properties']:
                continue

            # export object classes
            for object_type in new_schema['properties']['data']['properties']['object_type']['enum']:
                new_schema['properties']['data']['description'] = new_schema['description']
                write_cs_class(new_schema['properties']
                               ['data'], object_type, 'objects')

        # export attribute classes
        for prop in attr_schema:
            if attr_schema[prop]['type'] == 'object':
                write_cs_class(attr_schema[prop], prop, 'attributes')

        data_schema = {}
        data_schema['description'] = "Wraps all attributes in JSON."
        data_schema['properties'] = collections.OrderedDict(
            sorted(attr_schema.items()))

        # export data class
        write_cs_class(data_schema, 'data', 'attributes')


def write_cs_class(prop_schema, prop_name, tag_name):
    if 'properties' in prop_schema:
        prop_schema['properties'] = collections.OrderedDict(
            sorted(prop_schema['properties'].items()))
    prop_class = f"Arena{pascalcase(prop_name)}Json"
    prop_ns = snakecase(prop_name)
    if tag_name == 'objects':
        obj_classes[prop_ns] = prop_class
    cs_path = os.path.join(output_folder, f'{prop_class}.cs')

    # add object class
    with open(f'templates/cs_{tag_name}_class.j2') as tfile:
        t = Template(tfile.read())
    class_out = t.render(prop_schema=prop_schema,
                         prop_class=prop_class,
                         prop_name=prop_name,
                         pascalcase=pascalcase,
                         jstype2cstype=jstype2cstype,
                         jsenum2str=jsenum2str,
                         format_value=format_value,
                         )
    pfile = open(cs_path, 'w')
    pfile.write(f'{class_out}\n')
    pfile.close()


if __name__ == '__main__':
    main()
