import json
import os

from mdutils.mdutils import MdUtils

input_folder = 'schemas/'
output_folder = 'docs/'
#markdown_filename =

ObjTypeDesc = {
    'object': 'AFrame 3D Object',
    'program': 'ARENA program data',
    'scene-options': 'ARENA scene options',
    'landmarks': 'ARENA landmarks'
}

class Table:
    heading = ["Attribute", "Type", "Default", "Description", "Required"]
    cols = type('Columns', (object,), {
        'ATTR': 0,
        'TYPE': 1,
        'DFT': 2,
        'DESC': 3,
        'REQ': 4
    })()

def format_value(obj, value):
    type = 'object'
    if 'type' in obj:
        type = obj['type']
    if type == 'string':
        return f'```\'{value}\'```'
    return f'```{value}```'

def object_table(mdFile, md_title, obj, definitions={}):
    if 'properties' not in obj:
        return
    prop_list=obj['properties']
    required=[]
    default=[]
    if 'definitions' in obj:
        definitions = obj['definitions']
    if 'required' in obj:
        required=obj['required']
    if 'default' in obj:
        default=obj['default']
    table_lines = Table.heading.copy()
    for prop in prop_list:
        prop_obj = prop_list[prop]
        line = [''] * 5
        line[Table.cols.ATTR] = prop
        line[Table.cols.REQ] = 'No'
        if 'type' in prop_obj:
            line[Table.cols.TYPE] = prop_obj['type']
        if (prop == 'data'):
            line[Table.cols.DESC] = f'{md_title} object data properties as defined below'
            line[Table.cols.REQ] = 'Yes'
            line[Table.cols.TYPE] = f'{md_title} data'
        elif 'default' in prop_obj:
            line[Table.cols.DFT] = format_value(prop_obj, prop_obj["default"])
        if 'description' in prop_obj:
            line[Table.cols.DESC] = prop_obj['description'].replace(' (derived from \'type\' select above)', '')
        elif 'title' in prop_obj:
            line[Table.cols.DESC] = prop_obj['title']
        else:
            line[Table.cols.DESC] = prop
        if 'enum' in prop_obj:
            if (len(prop_obj["enum"]) == 1):
                type = prop_obj["enum"][0]
                if type in ObjTypeDesc:
                    line[Table.cols.DESC] = ObjTypeDesc[type]
                line[Table.cols.TYPE] = f'{line[Table.cols.TYPE]}; Must be: ```{type}```'
                line[Table.cols.DFT] = format_value(prop_obj, type)
            else:
                line[Table.cols.TYPE] = f'{line[Table.cols.TYPE]}; One of: ```{prop_obj["enum"]}```'
        if prop in required:
            line[Table.cols.REQ] = 'Yes'
        if prop in default:
            line[Table.cols.DFT] = format_value(default, default[prop])
        if '$ref' in prop_obj:
            obj_name = prop_obj['$ref'][len('#/definitions/'):]
            if obj_name in definitions and 'description' in definitions[obj_name]:
                line[Table.cols.DESC] = definitions[obj_name]['description'].split('\n')[0]
            else:
                line[Table.cols.DESC] = obj_name
            line[Table.cols.TYPE] = f'[{obj_name}]({obj_name})'
            if obj_name in definitions:
                write_md(definitions[obj_name], f'{output_folder}{obj_name}.md', overwrite=False, wire_obj=False)
        table_lines.extend(line)

    mdFile.new_table(columns=len(Table.heading), rows=len(table_lines)//len(Table.heading), text=table_lines, text_align='left')

def write_md(json_obj, md_fn, overwrite=True, wire_obj=True):
    if (not overwrite):
        if (os.path.isfile(md_fn)):
            return;
    print('->', md_fn)

    md_title = json_obj['title']
    mdFile = MdUtils(file_name=md_fn,title=md_title)

    desc = md_title
    if 'description' in json_obj:
        desc = json_obj['description']
    mdFile.new_paragraph(desc);

    if wire_obj:
        mdFile.new_paragraph('All wire objects have a set of basic attributes ```{object_id, action, type, persist, data}```. The ```data``` attribute defines the object-specific attributes');

    mdFile.new_header(level=2, title=f'\n{md_title} Attributes', style='setext', add_table_of_contents='n')

    object_table(mdFile, md_title, json_obj)

    if not 'properties' in json_obj:
        mdFile.create_md_file()
        return

    if not 'data' in json_obj['properties']:
        mdFile.create_md_file()
        return

    mdFile.new_header(level=3, title=f'{md_title} Data Attributes', add_table_of_contents='n')

    if '$ref' in json_obj['properties']['data']:
        obj_name = json_obj['properties']['data']['$ref'][len('#/definitions/'):]
        object_table(mdFile, md_title, json_obj['definitions'][obj_name], json_obj['definitions'])
    else:
        object_table(mdFile, md_title, json_obj['properties']['data'], json_obj['definitions'])

    mdFile.create_md_file()

def main():

    dir = os.fsencode(input_folder)

    for file in os.listdir(dir):
         filename = os.fsdecode(file)
         if filename.endswith(".json") and not filename.endswith("arena-schema-files.json"):
             json_filename = os.path.join(input_folder, filename)
             filename_noext = os.fsdecode(os.path.splitext(file)[0])
             md_filename = os.path.join(output_folder, f'{filename_noext}.md')
             with open(json_filename) as f:
                json_obj = json.load(f)
             write_md(json_obj, md_filename)
             continue
         else:
             continue

if __name__ == "__main__":
    main()
