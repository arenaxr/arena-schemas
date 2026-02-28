import os
import json
import glob
import re
import jinja2
import num2words
from caseconverter import pascalcase, snakecase
from .base import BaseGenerator
from .update import SchemaUpdater

ObjTypeDesc = {
    "object": "AFrame 3D Object",
    "program": "ARENA program data",
    "scene-options": "ARENA scene options",
    "landmarks": "ARENA landmarks",
    "camera-override": "ARENA camera override data",
}

class DotnetGenerator(BaseGenerator):
    """Generates schema classes in C# for ARENA-Unity."""

    def __init__(self, src, dst, **kwargs):
        super().__init__(**kwargs)
        self.src = src
        self.dst = dst
        self.updater = SchemaUpdater(src)

    def _enumcase(self, word):
        if word and word[0:1].isdigit():
            # convert if first char is a number, which is an illegal enum name in cs
            sub_words = re.split(r"(\d+)", word)
            def wordify(txt):
                if txt.isnumeric(): return num2words.num2words(txt)
                return txt
            num2worded = "-".join(list(map(lambda x: wordify(x), sub_words)))
            return pascalcase(num2worded)
        else:
            return pascalcase(word)

    def _jstype2cstype(self, prop):
        jstype = prop.get("type")
        ref = prop.get("$ref")
        default = prop.get("default")
        nulldec = "" if default is not None else "?"

        if jstype == "number": return f"float{nulldec}"
        elif jstype == "integer": return f"int{nulldec}"
        elif jstype == "boolean": return f"bool{nulldec}"
        elif jstype == "string": return "string"
        elif jstype == "array":
            items = prop.get("items", {})
            return f'{self._jstype2cstype(items)}[]'
        else:
            if ref:
                ref_name = pascalcase(ref.split("/")[-1])
                return f"Arena{ref_name}Json"
            return "object"

    def _format_value_cs(self, prop):
        jstype = prop.get("type")
        ref = prop.get("$ref")
        default = prop.get("default")
        items = prop.get("items")

        if default is None: return "null"
        if jstype == "string": return f'"{str(default)}"'
        elif jstype == "boolean": return f"{str(default).lower()}"
        elif jstype == "number": return f"{float(default):g}f"
        elif jstype == "integer": return f"{int(default)}"
        elif jstype == "array":
            array = []
            items_type = items.get("type") if items else None
            for item in default:
                if items_type == "object":
                    array.append(self._format_value_cs({"type": items_type, "default": str(json.dumps(item))}))
                else:
                    array.append(self._format_value_cs({"type": items_type, "default": str(item)}))
            return f'{{ {", ".join(array)} }}'
        else:
            default_json = str(default).replace('"', "'")
            if ref:
                ref_name = pascalcase(ref.split("/")[-1])
                return f'JsonConvert.DeserializeObject<Arena{ref_name}Json>("{default_json}")'
            return f'JsonConvert.DeserializeObject("{default_json}")'

    def _definition_py_cs(self, name, prop):
        title = prop.get("title")
        description = prop.get("description")
        if description: return description.replace("\n", " ").replace("  ", " ")
        elif title: return title
        else: return name

    def _write_cs_class(self, prop_schema, prop_name, tag_name, output_folder, obj_classes):
        prop_class = f"Arena{pascalcase(prop_name)}Json"
        prop_ns = snakecase(prop_name)
        if tag_name == "objects":
            obj_classes[prop_ns] = prop_class

        cs_path = os.path.join(output_folder, f"{prop_class}.cs")

        with open(f"templates/cs_{tag_name}_class.j2") as tfile:
            t = jinja2.Template(tfile.read())

        class_out = t.render(
            prop_schema=prop_schema,
            prop_class=prop_class,
            prop_name=prop_name,
            pascalcase=pascalcase,
            enumcase=self._enumcase,
            jstype2cstype=self._jstype2cstype,
            format_value=self._format_value_cs,
            definition=self._definition_py_cs,
        )
        print(f"->{cs_path}")
        with open(cs_path, "w") as pfile:
            pfile.write(f"{class_out}\n")

    def build(self):
        print(f"Generating C# schemas from {self.src} to {self.dst}")

        # Clean dest
        for oldpath in glob.iglob(os.path.join(self.dst, "*.cs")):
            os.remove(oldpath)

        os.makedirs(self.dst, exist_ok=True)

        list_fns = ["schemas/arena-schema-files.json", "schemas/arena-schema-files-nonpersist.json"]

        obj_schemas = {}
        obj_classes = {}
        attr_classes = {}
        obj_attr_schema = {}

        for list_fn in list_fns:
            obj_schema_path = os.path.join(self.src, list_fn)
            if not os.path.exists(obj_schema_path): continue
            with open(obj_schema_path) as tfile:
                obj_schemas.update(json.load(tfile))

            for _, obj_schema in obj_schemas.items():
                fn = obj_schema["file"]
                with open(os.path.join(self.src, fn)) as tfile:
                    schema = json.load(tfile)

                if "allOf" in schema:
                    new_schema = self.updater._parse_allof_ref(schema, expand_refs=True, attr_classes=attr_classes, obj_attr_schema=obj_attr_schema)
                    del schema["allOf"]
                else:
                    new_schema = schema

                if "data" in new_schema.get("properties", {}) and "allOf" in new_schema["properties"]["data"]:
                    new_schema["properties"]["data"] = self.updater._parse_allof_ref(
                        new_schema["properties"]["data"], expand_refs=False, attr_classes=attr_classes, obj_attr_schema=obj_attr_schema
                    )
                    del new_schema["properties"]["data"]["allOf"]

                if "data" in new_schema.get("properties", {}) and "$ref" in new_schema["properties"]["data"]:
                    key = new_schema["properties"]["data"]["$ref"].split("/")[-1]
                    new_schema["properties"]["data"] = new_schema["definitions"][key]

                # generate definitions
                if "definitions" not in new_schema:
                    new_schema["definitions"] = {}
                if "data" in new_schema.get("properties", {}) and "properties" in new_schema["properties"]["data"]:
                    dprops = new_schema["properties"]["data"]["properties"]
                    for key in dprops:
                        if "type" in dprops[key] and dprops[key]["type"] == "object" and "deprecated" not in dprops[key]:
                            if key not in new_schema["definitions"]:
                                new_schema["definitions"][key] = dprops[key]
                                new_schema["properties"]["data"]["properties"][key] = {"$ref": f"#/definitions/{key}"}

                if "data" not in new_schema.get("properties", {}) or "properties" not in new_schema["properties"]["data"]:
                    continue

                new_schema["properties"]["data"]["description"] = self._definition_py_cs(new_schema.get("type", ""), new_schema)
                if "object_type" in new_schema["properties"]["data"]["properties"]:
                    for object_type in new_schema["properties"]["data"]["properties"]["object_type"]["enum"]:
                        self._write_cs_class(new_schema["properties"]["data"], object_type, "objects", self.dst, obj_classes)
                else:
                    prop_name = os.path.splitext(os.path.basename(fn))[0]
                    self._write_cs_class(new_schema["properties"]["data"], prop_name, "attributes", self.dst, obj_classes)
                    for prop in new_schema["properties"]["data"]["properties"]:
                        if "$ref" in new_schema["properties"]["data"]["properties"][prop]:
                            key = new_schema["properties"]["data"]["properties"][prop]["$ref"].split("/")[-1]
                            self._write_cs_class(new_schema.get("definitions", {}).get(key, {}), key, "attributes", self.dst, obj_classes)

            for prop in obj_attr_schema:
                if "type" in obj_attr_schema[prop] and obj_attr_schema[prop]["type"] in ObjTypeDesc:
                    self._write_cs_class(obj_attr_schema[prop], prop, "attributes", self.dst, obj_classes)

            data_schema = {
                "description": "Wraps all attributes in JSON.",
                "properties": obj_attr_schema
            }

            self._write_cs_class(data_schema, "data", "attributes", self.dst, obj_classes)
