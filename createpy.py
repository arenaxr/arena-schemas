import collections
import json
import os
import sys

from caseconverter import pascalcase, snakecase
from jinja2 import Template

output_folder = ''
input_folder = ''


def jstype2pytype(jstype):
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
        return "list"
    elif jstype == "object":
        return "dict"
    else:
        return "dict"


def jsenum2str(prop):
    if 'enum' in prop:
        s = ', '
        items = s.join(prop['enum'])
        return f' [{items}]'
    return ''


def parse_allof_ref(allof_schema, expand_refs=True):
    global input_folder, attr_classes
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
        print('Supply a valid destination  schemas path! dst=arena-py/arena')
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

            for type in new_schema['properties']['data']['properties']['object_type']['enum']:
                obj_type = type
                obj_class = pascalcase(obj_type)
                obj_ns = snakecase(obj_type)
                obj_classes[obj_ns] = obj_class
                obj_path = os.path.join(output_folder, 'objects', f'{obj_ns}.py')

                # add object class if needed
                if not os.path.isfile(obj_path):
                    with open('templates/py_object_class.j2') as tfile:
                        t = Template(tfile.read())
                    class_out = t.render(obj_schema=new_schema,
                                         obj_class=obj_class, obj_type=obj_type)
                    pfile = open(obj_path, 'w')
                    pfile.write(f'{class_out}\n')
                    pfile.close()

                # update the object docstring only
                pfile = open(obj_path, 'r')
                lines = pfile.readlines()
                pfile.close()
                with open('templates/py_object_docstring.j2') as tfile:
                    t = Template(tfile.read())
                    t.globals['jstype2pytype'] = jstype2pytype
                    t.globals['jsenum2str'] = jsenum2str
                docstr_out = t.render(obj_schema=new_schema,
                                      obj_class=obj_class, obj_type=obj_type)
                class_dec = f'class {obj_class}('
                pfile = open(obj_path, 'w')
                found_class = False
                found_doc = False
                for line in lines:
                    if line.startswith(class_dec):
                        found_class = True
                        pfile.write(line)
                    elif found_class and '"""' in line:
                        found_class = False
                        found_doc = True
                        pfile.write(f'{docstr_out}\n')
                    elif found_doc:
                        if '"""' in line:
                            found_doc = False
                    else:
                        pfile.write(line)
                pfile.close()

        # sort objects
        obj_classes = collections.OrderedDict(sorted(obj_classes.items()))
        attr_classes = collections.OrderedDict(sorted(attr_classes.items()))

        # export objects init file
        with open('templates/py_object_init.j2') as tfile:
            t = Template(tfile.read())
        pfile = open(os.path.join(output_folder, 'objects', '__init__.py'), 'w')
        init_out = t.render(classes=obj_classes)
        pfile.write(f'{init_out}\n')
        pfile.close()

        # export attributes init file
        with open('templates/py_attribute_init.j2') as tfile:
            t = Template(tfile.read())
        pfile = open(os.path.join(output_folder, 'attributes', '__init__.py'), 'w')
        init_out = t.render(classes=attr_classes)
        pfile.write(f'{init_out}\n')
        pfile.close()


if __name__ == '__main__':
    main()
