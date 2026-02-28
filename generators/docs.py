import os
import json
from mdutils.mdutils import MdUtils
from .base import BaseGenerator

ObjTypeDesc = {
    "object": "AFrame 3D Object",
    "program": "ARENA program data",
    "scene-options": "ARENA scene options",
    "landmarks": "ARENA landmarks",
    "camera-override": "ARENA camera override data",
}

class Table:
    heading = ["Attribute", "Type", "Default", "Description", "Required"]
    cols = type("Columns", (object,), {"ATTR": 0, "TYPE": 1, "DFT": 2, "DESC": 3, "REQ": 4})()

def format_value_doc(obj, value):
    obj_type = obj.get("type", "object")
    if obj_type == "string":
        return f"```'{value}'```"
    return f"```{value}```"

class MarkdownGenerator(BaseGenerator):
    """Generates standard Markdown tables."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.input_folder = "schemas"
        self.output_folder = "docs"

    def _object_table(self, mdFile, md_title, obj, output_folder, definitions=None):
        if definitions is None:
            definitions = {}
        prop_list = {}
        if "properties" in obj:
            prop_list.update(obj["properties"])
        if "patternProperties" in obj:
            prop_list.update(obj["patternProperties"])
        if not prop_list:
            return

        required = obj.get("required", [])
        default = obj.get("default", [])
        definitions = obj.get("definitions", definitions)
        table_lines = Table.heading.copy()

        for prop, prop_obj in prop_list.items():
            line = [""] * 5
            line[Table.cols.ATTR] = f"**{prop}**"
            line[Table.cols.REQ] = "No"
            if "type" in prop_obj:
                line[Table.cols.TYPE] = prop_obj["type"]

            if prop == "data":
                line[Table.cols.DESC] = f"{md_title} object data properties as defined below"
                line[Table.cols.REQ] = "Yes"
                line[Table.cols.TYPE] = f"{md_title} data"
            elif "default" in prop_obj:
                line[Table.cols.DFT] = format_value_doc(prop_obj, prop_obj["default"])

            if "description" in prop_obj:
                line[Table.cols.DESC] = prop_obj["description"].replace(" (derived from 'type' select above)", "")
            elif "title" in prop_obj:
                line[Table.cols.DESC] = prop_obj["title"]
            else:
                line[Table.cols.DESC] = prop

            if "enum" in prop_obj:
                if len(prop_obj["enum"]) == 1:
                    type_val = prop_obj["enum"][0]
                    if type_val in ObjTypeDesc:
                        line[Table.cols.DESC] = ObjTypeDesc[type_val]
                    line[Table.cols.TYPE] = f"{line[Table.cols.TYPE]}; Must be: ```{type_val}```"
                    line[Table.cols.DFT] = format_value_doc(prop_obj, type_val)
                else:
                    line[Table.cols.TYPE] = f'{line[Table.cols.TYPE]}; One of: ```{prop_obj["enum"]}```'

            if prop in required:
                line[Table.cols.REQ] = "Yes"
            if isinstance(default, dict) and prop in default:
                line[Table.cols.DFT] = format_value_doc(prop_obj, default[prop])

            if "$ref" in prop_obj:
                obj_name = prop_obj["$ref"][len("#/definitions/") :]
                if obj_name in definitions and "description" in definitions[obj_name]:
                    line[Table.cols.DESC] = definitions[obj_name]["description"].split("\n")[0]
                line[Table.cols.TYPE] = f"[{obj_name}]({obj_name})"
                if obj_name in definitions:
                    self._write_md(
                        definitions[obj_name],
                        os.path.join(output_folder, f"{obj_name}.md"),
                        obj_name,
                        overwrite=False,
                        wire_obj=False,
                    )

            if "deprecated" in prop_obj:
                for col in range(Table.cols.REQ + 1):
                    if line[col]:
                        line[col] = f"~~{line[col]}~~"
            elif prop_obj.get("type") == "object" and "properties" in obj:
                self._write_md(
                    obj["properties"][prop],
                    os.path.join(output_folder, f"{prop}.md"),
                    prop,
                    overwrite=True,
                    wire_obj=False,
                )

            table_lines.extend(line)

        mdFile.new_table(
            columns=len(Table.heading), rows=len(table_lines) // len(Table.heading), text=table_lines, text_align="left"
        )

    def _write_md(self, json_obj, md_fn, object_name, overwrite=True, wire_obj=True):
        if not overwrite and os.path.isfile(md_fn):
            return

        print("->", md_fn)
        title = json_obj.get("title", object_name)
        mdFile = MdUtils(file_name=md_fn, title=f"`{object_name}`")

        schema_desc = f"This is the schema for {title}, the properties of {'wire object type' if wire_obj else 'object'} `{object_name}`."
        desc = f"{json_obj['description']}\n\n{schema_desc}" if "description" in json_obj else schema_desc
        mdFile.new_paragraph(desc)

        if wire_obj:
            mdFile.new_paragraph(
                "All wire objects have a set of basic attributes ```{object_id, action, type, persist, data}```. The ```data``` attribute defines the object-specific attributes"
            )

        mdFile.new_header(level=2, title=f"\n{title} Attributes", style="setext", add_table_of_contents="n")
        self._object_table(mdFile, title, json_obj, self.output_folder)

        if "example" in json_obj:
            mdFile.new_header(level=2, title=f"\n{title} Example", style="setext", add_table_of_contents="n")
            mdFile.insert_code(code=json.dumps(json_obj["example"], indent=4), language="json")

        if "properties" in json_obj and "data" in json_obj["properties"]:
            mdFile.new_header(level=3, title=f"{title} Data Attributes", add_table_of_contents="n")

            data_prop = json_obj["properties"]["data"]
            if "$ref" in data_prop:
                obj_name = data_prop["$ref"][len("#/definitions/") :]
                self._object_table(mdFile, title, json_obj["definitions"][obj_name], self.output_folder, json_obj.get("definitions", {}))
            else:
                self._object_table(mdFile, title, data_prop, self.output_folder, json_obj.get("definitions", {}))

        mdFile.create_md_file()

    def build(self):
        print(f"Generating docs from {self.input_folder}/ to {self.output_folder}/")
        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)

        for filename in os.listdir(self.input_folder):
            if filename.endswith(".json") and not filename.startswith("arena-schema-files"):
                json_filename = os.path.join(self.input_folder, filename)
                filename_noext = os.path.splitext(filename)[0]
                md_filename = os.path.join(self.output_folder, f"{filename_noext}.md")

                with open(json_filename, 'r') as f:
                    try:
                        json_obj = json.load(f)
                    except Exception as e:
                        print(f"Error loading {json_filename}: {e}")
                        continue

                prefix_removed = filename_noext[6:] if filename_noext.startswith("arena-") else filename_noext
                self._write_md(json_obj, md_filename, prefix_removed)
