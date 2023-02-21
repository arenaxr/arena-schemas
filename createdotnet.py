import json
import os
from caseconverter import pascalcase

#from mdutils.mdutils import MdUtils

input_folder = 'schemas/'
output_folder = 'dotnet/'

ObjTypeDesc = {
    'object': 'AFrame 3D Object',
    'program': 'ARENA program data',
    'scene-options': 'ARENA scene options',
    'landmarks': 'ARENA landmarks'
}


class Table:
    heading = ["Attribute", "Type", "Default", "Description", "Required", "Enum"]
    cols = type('Columns', (object,), {
        'ATTR': 0,
        'TYPE': 1,
        'DFT': 2,
        'DESC': 3,
        'REQ': 4,
        'ENUM': 5
    })()


def format_value(obj, value):
    type = 'object'
    if 'type' in obj:
        type = obj['type']
    if type == 'string':
        return f'\"{value}\"'
    if type == 'boolean':
        return f'{str(value).lower()}'
    return f'{value}'


# def object_table(mdFile, cs_title, obj, definitions={}):
def object_table(cs_title, obj, definitions={}):
    cs_lines = []
    if 'properties' not in obj:
        return
    prop_list = obj['properties']
    required = []
    default = []
    if 'definitions' in obj:
        definitions = obj['definitions']
    if 'required' in obj:
        required = obj['required']
    if 'default' in obj:
        default = obj['default']
    table_lines = Table.heading.copy()
    for prop in prop_list:
        prop_obj = prop_list[prop]
        line = [''] * 6
        line[Table.cols.ATTR] = prop
        pascalAttrName = pascalcase(line[Table.cols.ATTR])
        line[Table.cols.REQ] = 'No'
        if 'type' in prop_obj:
            line[Table.cols.TYPE] = get_cs_type(prop_obj['type'])
        if prop == 'data':
            line[Table.cols.DESC] = f'{cs_title} object data properties as defined below'
            line[Table.cols.REQ] = 'Yes'
            line[Table.cols.TYPE] = f'{cs_title} data'
        elif 'default' in prop_obj:
            line[Table.cols.DFT] = format_value(prop_obj, prop_obj["default"])
        if 'description' in prop_obj:
            line[Table.cols.DESC] = prop_obj['description'].replace(
                ' (derived from \'type\' select above)', '')
        elif 'title' in prop_obj:
            line[Table.cols.DESC] = prop_obj['title']
        else:
            line[Table.cols.DESC] = prop
        if 'enum' in prop_obj:
            if len(prop_obj["enum"]) == 1:
                type = prop_obj["enum"][0]
                if type in ObjTypeDesc:
                    line[Table.cols.DESC] = ObjTypeDesc[type]
                line[Table.cols.TYPE] = f'{line[Table.cols.TYPE]}; Must be: ```{type}```'
                line[Table.cols.DFT] = format_value(prop_obj, type)
            else:
                #line[Table.cols.TYPE] = f'{line[Table.cols.TYPE]}; One of: ```{prop_obj["enum"]}```'
                line[Table.cols.ENUM] = prop_obj["enum"]
                line[Table.cols.TYPE] = f'{pascalAttrName}Type'
        if prop in required:
            line[Table.cols.REQ] = 'Yes'
        if prop in default:
            line[Table.cols.DFT] = format_value(default, default[prop])
        if '$ref' in prop_obj:
            obj_name = prop_obj['$ref'][len('#/definitions/'):]
            if obj_name in definitions and 'description' in definitions[obj_name]:
                line[Table.cols.DESC] = definitions[obj_name]['description'].split('\n')[
                    0]
            else:
                line[Table.cols.DESC] = obj_name
            line[Table.cols.TYPE] = f'[{obj_name}]({obj_name})'
            if obj_name in definitions:
                write_cs(
                    definitions[obj_name], obj_name, f'{output_folder}{obj_name}.cs', overwrite=False, wire_obj=False)
        table_lines.extend(line)

        cs_lines.append('\n')
        if (line[Table.cols.ENUM]):
            cs_lines.append(f'        public enum {line[Table.cols.TYPE]}\n')
            cs_lines.append('        {\n')
            for enumVal in line[Table.cols.ENUM]:
                cs_lines.append(f'            [EnumMember(Value = "{enumVal}")]\n')
                cs_lines.append(f'            {enumVal},\n')
            cs_lines.append('        }\n')
        if (line[Table.cols.ENUM]):
            cs_lines.append(f'        private const {line[Table.cols.TYPE]} def{pascalAttrName} = {pascalAttrName}Type.{line[Table.cols.DFT]};\n')
            cs_lines.append(f'        [JsonConverter(typeof(StringEnumConverter))]\n')
        else:
            cs_lines.append(f'        private const {line[Table.cols.TYPE]} def{pascalAttrName} = {line[Table.cols.DFT]};\n')
        cs_lines.append(f'        [JsonProperty(PropertyName="{line[Table.cols.ATTR]}")]\n')
        cs_lines.append(f'        [Tooltip("{line[Table.cols.DESC]}")]\n')
        cs_lines.append(f'        public {line[Table.cols.TYPE]} {pascalAttrName} = def{pascalAttrName};\n')
        cs_lines.append(f'        public bool ShouldSerialize{pascalAttrName}()\n')
        cs_lines.append('        {\n')
        if line[Table.cols.REQ] == 'Yes':
            cs_lines.append(f'            return true; // required in json schema \n')
        else:
            cs_lines.append(f'            if (_token != null && _token.SelectToken("{line[Table.cols.ATTR]}") != null) return true;\n')
            cs_lines.append(f'            return ({pascalAttrName} != def{pascalAttrName});\n')
        cs_lines.append('        }\n')


    # mdFile.new_table(columns=len(Table.heading), rows=len(
    #     table_lines)//len(Table.heading), text=table_lines, text_align='left')
    return cs_lines

def get_cs_type(type):
    if type == "number":
        return "float"
    elif type == "integer":
        return "int"
    elif type == "boolean":
        return "bool"
    return type


def cs_pre(cs_class, prop, desc):
    return f'''/**
 * Open source software under the terms in /LICENSE
 * Copyright (c) 2021-2023, Carnegie Mellon University. All rights reserved.
 */

using System;
using System.Collections.Generic;
using System.Runtime.Serialization;
using System.Text.RegularExpressions;
using Newtonsoft.Json;
using Newtonsoft.Json.Converters;
using Newtonsoft.Json.Linq;
using UnityEngine;

namespace ArenaUnity.Schemas
{{
    /// <summary>
    /// {desc}
    /// </summary>
    [Serializable]
    public class {cs_class}
    {{
        public const string componentName = "{prop}";

        // {cs_class} Member-fields
'''

def cs_post(cs_class):
    return f'''
        // General json object management

        [JsonExtensionData]
        private IDictionary<string, JToken> _additionalData;

        private static JToken _token;

        public string SaveToString()
        {{
            return Regex.Unescape(JsonConvert.SerializeObject(this));
        }}

        public static {cs_class} CreateFromJSON(string jsonString, JToken token)
        {{
            _token = token; // save updated wire json
            return JsonConvert.DeserializeObject<{cs_class}>(Regex.Unescape(jsonString));
        }}
    }}
}}
'''


def write_cs(json_obj, obj_name, cs_fn, overwrite=True, wire_obj=True):
    if not overwrite:
        if os.path.isfile(cs_fn):
            return
    print('->', cs_fn)

    cs_title = json_obj['title']
    # mdFile = MdUtils(file_name=cs_fn, title=cs_title)

    cs_lines = []

    desc = cs_title
    if 'description' in json_obj:
        desc = json_obj['description']
    # mdFile.new_paragraph(desc)
    desc = desc.replace('\n','')

    print(obj_name)
    print(cs_title)
    cs_class = f'Arena{pascalcase(obj_name)}Json'
    cs_lines.append(cs_pre(cs_class, obj_name, desc))
    # if wire_obj:
    #     mdFile.new_paragraph(
    #         'All wire objects have a set of basic attributes ```{object_id, action, type, persist, data}```. The ```data``` attribute defines the object-specific attributes')

    # mdFile.new_header(
    #     level=2, title=f'\n{cs_title} Attributes', style='setext', add_table_of_contents='n')
    # cs_file_new_header(
    #     level=2, title=f'\n{cs_title} Attributes', style='setext', add_table_of_contents='n')

    cs_lines.extend(object_table(cs_title, json_obj))

    if not 'properties' in json_obj:
        # mdFile.create_md_file()
        create_cs_file(cs_fn, cs_class, cs_lines)
        return

    if not 'data' in json_obj['properties']:
        # mdFile.create_md_file()
        create_cs_file(cs_fn, cs_class, cs_lines)
        return

    # mdFile.new_header(
    #     level=3, title=f'{cs_title} Data Attributes', add_table_of_contents='n')
    # cs_file_new_header(
    #     level=3, title=f'{cs_title} Data Attributes', add_table_of_contents='n')

    if '$ref' in json_obj['properties']['data']:
        obj_name = json_obj['properties']['data']['$ref'][len(
            '#/definitions/'):]
        cs_lines.extend(object_table(cs_title,
                                     json_obj['definitions'][obj_name], json_obj['definitions']))
    else:
        cs_lines.extend(object_table(cs_title,
                                     json_obj['properties']['data'], json_obj['definitions']))


    create_cs_file(cs_fn, cs_class, cs_lines)


def create_cs_file(cs_fn, cs_class, cs_lines):
    # mdFile.create_md_file()

    cs_lines.append(cs_post(cs_class))

    # cs_lines.append(text)
    out = ''.join(cs_lines)
    #cs_path = os.path.join(output_folder,  cs_fn)
    f = open(cs_fn, 'w')
    f.write(out)


def main():

    dir = os.fsencode(input_folder)

    for file in os.listdir(dir):
        filename = os.fsdecode(file)
        if filename.endswith(".json") and not filename.endswith("arena-schema-files.json"):
            json_filename = os.path.join(input_folder, filename)
            filename_noext = os.fsdecode(os.path.splitext(file)[0])
            cs_filename = os.path.join(output_folder, f'{filename_noext}.cs')
            with open(json_filename) as f:
                json_obj = json.load(f)
            write_cs(json_obj, filename_noext, cs_filename)
            continue
        else:
            continue


if __name__ == "__main__":
    main()