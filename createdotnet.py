import json
import os
import sys

import num2words
from caseconverter import camelcase, pascalcase

input_folder = 'schemas'
output_folder = 'dotnet'

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
    elif type == 'boolean':
        return f'{str(value).lower()}'
    elif type == 'number':
        return f'{"{0:g}".format(float(value))}'
    elif type == 'integer':
        return f'{int(value)}'
    elif type == 'array':
        format_array = str(value).replace("[","{").replace("]","}").replace("'", "\"")
        #print(format_array)
        return f'{format_array}'
    return f'{value}'


def object_table(cs_title, obj, wire_obj, definitions={}):
    cs_lines = []
    prop_list = {}
    if 'properties' in obj:
        prop_list.update(obj['properties'])
    if 'patternProperties' in obj:
        prop_list.update(obj['patternProperties'])
    if prop_list == {}:
        return
    required = []
    default = []
    if 'definitions' in obj:
        definitions = obj['definitions']
    if 'required' in obj:
        required = obj['required']
    if 'default' in obj:
        default = obj['default']
    table_lines = Table.heading.copy()
    for prop, prop_obj in prop_list.items():
        prop_obj = prop_list[prop]
        if 'deprecated' in prop_obj:
            continue  # stop processing deprecated properties
        line = [''] * 6
        line[Table.cols.ATTR] = prop
        pascalAttrName = pascalcase(line[Table.cols.ATTR])
        camelAttrName = camelcase(line[Table.cols.ATTR])
        line[Table.cols.REQ] = 'No'
        if 'type' in prop_obj:
            line[Table.cols.TYPE] = get_cs_type(prop_obj)
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
                #line[Table.cols.TYPE] = f'{line[Table.cols.TYPE]}; Must be: ```{type}```'
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
            #line[Table.cols.TYPE] = f'[{obj_name}]({obj_name})'
            line[Table.cols.TYPE] = 'object'
            if obj_name in definitions:
                cs_class = f'Arena{pascalcase(obj_name)}Json'
                write_cs(
                    definitions[obj_name], obj_name, cs_class, overwrite=False, wire_obj=False)
        table_lines.extend(line)

        if prop == 'object_type':
            continue  # stop processing object_type, remove from cs
        if prop == 'parent':
            break  # stop processing after parent, remove from cs

        cs_lines.append('\n')
        if (line[Table.cols.ENUM]):
            cs_lines.append(f'        public enum {line[Table.cols.TYPE]}\n')
            cs_lines.append('        {\n')
            for enumVal in line[Table.cols.ENUM]:
                cs_lines.append(f'            [EnumMember(Value = "{enumVal}")]\n')
                cs_lines.append(f'            {enumcase(enumVal)},\n')
            cs_lines.append('        }\n')
        defValue = str(line[Table.cols.DFT])#.replace("\"","")
        if (line[Table.cols.ENUM]):
            cs_lines.append(f'        private static {line[Table.cols.TYPE]} def{pascalAttrName} = {pascalAttrName}Type.{enumcase(defValue)};\n')
            cs_lines.append(f'        [JsonConverter(typeof(StringEnumConverter))]\n')
        else:
            if line[Table.cols.TYPE] == "string":
                defValue = f'"{defValue}"'.replace("\"\"", "\"")
                if defValue == '"':
                    defValue = f'""'
            elif line[Table.cols.TYPE] == "float":
                defValue = f'{defValue}f'
            elif line[Table.cols.TYPE] == "bool":
                defValue = f'{defValue.lower()}'
            elif line[Table.cols.TYPE] == "object":
                defValue = f'JsonConvert.DeserializeObject("{defValue}")'
            elif line[Table.cols.TYPE].endswith("[]"):
                #print (defValue)
                defValue = f'{defValue}'
            cs_lines.append(f'        private static {line[Table.cols.TYPE]} def{pascalAttrName} = {defValue};\n')
        cs_lines.append(f'        [JsonProperty(PropertyName = "{line[Table.cols.ATTR]}")]\n')
        cs_lines.append(f'        [Tooltip("{line[Table.cols.DESC]}")]\n')
        cs_lines.append(f'        public {line[Table.cols.TYPE]} {pascalAttrName} = def{pascalAttrName};\n')
        cs_lines.append(f'        public bool ShouldSerialize{pascalAttrName}()\n')
        cs_lines.append('        {\n')
        if line[Table.cols.REQ] == 'Yes':
            cs_lines.append(f'            return true; // required in json schema\n')
        else:
            cs_lines.append(f'            // {prop}\n')
            cs_lines.append(f'            return ({pascalAttrName} != def{pascalAttrName});\n')
        cs_lines.append('        }\n')

    return cs_lines


def enumcase(word):
    word = word.replace("\"", "")
    if word and word[0:1].isdigit():
        return pascalcase(num2words.num2words(word[0:1])+word[1:])
    else:
        return pascalcase(word)


def get_cs_type(prop_obj):
    if prop_obj['type'] == "number":
        return "float"
    elif prop_obj['type'] == "integer":
        return "int"
    elif prop_obj['type'] == "boolean":
        return "bool"
    elif prop_obj['type'] == "array":
        if "items" in prop_obj and "type" in prop_obj['items']:
            array_type = get_cs_type(prop_obj['items'])
            return f"{array_type}[]"
        else:
            return "string[]"

    return prop_obj['type']


def cs_pre(cs_class, prop, desc):
    return f'''/**
 * Open source software under the terms in /LICENSE
 * Copyright (c) 2021-2023, Carnegie Mellon University. All rights reserved.
 */

// CAUTION: This file is autogenerated from https://github.com/arenaxr/arena-schemas. Changes made here may be overwritten.

using System;
using System.Collections.Generic;
using System.Runtime.Serialization;
using System.Text.RegularExpressions;
using Newtonsoft.Json;
using Newtonsoft.Json.Converters;
using Newtonsoft.Json.Linq;
using Newtonsoft.Json.Serialization;
using UnityEngine;

namespace ArenaUnity.Schemas
{{
    /// <summary>
    /// {desc}
    /// </summary>
    [Serializable]
    public class {cs_class}
    {{
        public readonly string object_type = "{prop}";

        // {prop} member-fields
'''
        # public readonly string object_type = "{prop}";
        # [JsonIgnore]
        # public readonly string componentName = "{prop}";


def cs_post(cs_class):
    return f'''
        // General json object management
        [OnError]
        internal void OnError(StreamingContext context, ErrorContext errorContext)
        {{
            Debug.LogWarning($"{{errorContext.Error.Message}}: {{errorContext.OriginalObject}}");
            errorContext.Handled = true;
        }}

        [JsonExtensionData]
        private IDictionary<string, JToken> _additionalData;
    }}
}}
'''


def write_cs(json_obj, obj_name, cs_class, overwrite=True, wire_obj=True):
    cs_fn = os.path.join(output_folder, f'{cs_class}.cs')
    if not overwrite:
        if os.path.isfile(cs_fn):
            return
    print('->', cs_fn)

    cs_title = json_obj['title']

    cs_lines = []

    desc = cs_title
    if 'description' in json_obj:
        desc = json_obj['description']
    desc = desc.replace('\n','')

    cs_lines.append(cs_pre(cs_class, obj_name, desc))
    # if wire_obj:
    #         'All wire objects have a set of basic attributes ```{object_id, action, type, persist, data}```. The ```data``` attribute defines the
    # cs_file_new_header(
    #     level=2, title=f'\n{cs_title} Attributes', style='setext', add_table_of_contents='n')

    if not wire_obj:
        cs_lines.extend(object_table(cs_title, json_obj, wire_obj))

    if not 'properties' in json_obj:
        create_cs_file(cs_fn, cs_class, cs_lines)
        return

    if not 'data' in json_obj['properties']:
        create_cs_file(cs_fn, cs_class, cs_lines)
        return

    # cs_file_new_header(
    #     level=3, title=f'{cs_title} Data Attributes', add_table_of_contents='n')

    if '$ref' in json_obj['properties']['data']:
        obj_name = json_obj['properties']['data']['$ref'][len(
            '#/definitions/'):]
        cs_lines.extend(object_table(cs_title,
                                     json_obj['definitions'][obj_name], wire_obj, json_obj['definitions']))
    else:
        cs_lines.extend(object_table(cs_title,
                                     json_obj['properties']['data'], wire_obj, json_obj['definitions']))

    # if not wire_obj: # TODO: for now do not write full wire objects, just the components
    #     create_cs_file(cs_fn, cs_class, cs_lines)
    create_cs_file(cs_fn, cs_class, cs_lines)


def create_cs_file(cs_fn, cs_class, cs_lines):

    cs_lines.append(cs_post(cs_class))

    # cs_lines.append(text)
    out = ''.join(cs_lines)
    #cs_path = os.path.join(output_folder,  cs_fn)
    f = open(cs_fn, 'w')
    f.write(out)


def main():
    global output_folder
    args = sys.argv[1:]
    print(args)
    if (len(args) == 0 or not os.path.isdir(args[0])):
        os.mkdir(args[0])

    output_folder = args[0]

    dir = os.fsencode(input_folder)

    for file in os.listdir(dir):
        filename = os.fsdecode(file)
        if filename.endswith(".json") and not filename.endswith("arena-schema-files.json"):
            json_filename = os.path.join(input_folder, filename)
            filename_noext = os.fsdecode(os.path.splitext(file)[0])
            cs_class = f'Arena{pascalcase(filename_noext)}Json'
            with open(json_filename) as f:
                json_obj = json.load(f)
            write_cs(json_obj, filename_noext, cs_class)
            continue
        else:
            continue


if __name__ == "__main__":
    main()
