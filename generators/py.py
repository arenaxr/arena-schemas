import os
import json
import collections
import jinja2
from caseconverter import pascalcase, snakecase
from .base import BaseGenerator
from .update import SchemaUpdater

class PythonGenerator(BaseGenerator):
    """
    Safely modifies Python class docstrings using Jinja2 templates for the docstring text,
    and a safe python source code modifier.
    """

    def __init__(self, src, dst, **kwargs):
        super().__init__(**kwargs)
        self.src = src
        self.dst = dst
        self.updater = SchemaUpdater(src)

    def _definition_py(self, name, prop):
        title = prop.get("title")
        description = prop.get("description")
        deprecated = prop.get("deprecated")
        define = description or title or name
        if deprecated:
            define = f"*{define}*"  # add italics
        return (
            define.replace("\n", " ")
            .replace("\\", "\\\\")
            .replace("  ", " ")
            .replace("<a href='", "<")
            .replace("'>", "> ")
            .replace("</a>", "")
            .replace("deprecated", "**deprecated**")
            .replace("DEPRECATED", "**DEPRECATED**")
        )

    def _jstype2pytype(self, jstype, arraytype):
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
            if arraytype is not None:
                return f"list[{self._jstype2pytype(arraytype, None)}]"
            else:
                return "list"
        elif jstype == "object":
            return "dict"
        else:
            return "dict"

    def _jsenum2str(self, prop):
        if "enum" in prop:
            s = ", "
            items = s.join(prop["enum"])
            return f" Allows [{items}]"
        return ""

    def _write_py_class(self, prop_schema, prop_name, tag_name, output_folder, attr_classes, obj_classes):
        AltUsages = {
            "click-listener": ["clickable=True"],
            "color": ["color=Color(red,green,blue)", "color=(red,green,blue)"],
            "position": ["position=Position(x,y,z)", "position=(x,y,z)"],
            "rotation": ["rotation=Rotation(x,y,z,w)", "rotation=Rotation(x,y,z)", "rotation=(x,y,z,w)", "rotation=(x,y,z)"],
            "scale": ["scale=Scale(x,y,z)", "scale=(x,y,z)"],
        }
        FirstIterable = ["color", "position", "rotation", "scale"]

        if "properties" in prop_schema:
            prop_schema["properties"] = collections.OrderedDict(sorted(prop_schema["properties"].items()))

        prop_class = pascalcase(prop_name)
        prop_ns = snakecase(prop_name)
        prop_dict = prop_name.replace("-", "_")

        uses = [f"`{prop_dict}={prop_class}(...)`"]
        if prop_name in AltUsages:
            for use in AltUsages[prop_name]:
                uses.append(f"`{use}`")
        prop_usage = " or ".join(uses)

        iterable = "|Iterable|Mapping" if prop_name in FirstIterable else None

        if tag_name == "objects":
            obj_classes[prop_ns] = prop_class

        py_dir = os.path.join(output_folder, tag_name)
        os.makedirs(py_dir, exist_ok=True)
        py_path = os.path.join(py_dir, f"{prop_ns}.py")

        # Create new class shell if missing
        if not os.path.isfile(py_path):
            with open(f"templates/py_{tag_name}_class.j2") as tfile:
                t = jinja2.Template(tfile.read())
            class_out = t.render(
                prop_schema=prop_schema,
                prop_dict=prop_dict,
                prop_class=prop_class,
                prop_name=prop_name,
                definition=self._definition_py,
            )
            print(f"->{py_path}")
            with open(py_path, "w") as pfile:
                pfile.write(f"{class_out}\n")

        # Render docstring
        with open(f"templates/py_{tag_name}_docstring.j2") as tfile:
            t = jinja2.Template(tfile.read())
            t.globals["jstype2pytype"] = self._jstype2pytype
            t.globals["jsenum2str"] = self._jsenum2str

        docstr_out = t.render(
            prop_schema=prop_schema,
            prop_dict=prop_dict,
            prop_class=prop_class,
            prop_name=prop_name,
            prop_usage=prop_usage,
            definition=self._definition_py,
            iterable=iterable,
        )

        # Non-destructive precise docstring replacement
        with open(py_path, "r") as pfile:
            lines = pfile.readlines()

        class_dec = f"class {prop_class}("
        print(f"->{py_path}")

        with open(py_path, "w") as pfile:
            found_class = False
            found_doc = False
            for line in lines:
                if line.startswith(class_dec) and not found_class:
                    found_class = True
                    pfile.write(line)
                elif found_class and '"""' in line and not found_doc:
                    found_class = False
                    found_doc = True
                    pfile.write(f"{docstr_out}\n")
                elif found_doc:
                    if '"""' in line:
                        found_doc = False # finished skipping old docstring
                else:
                    pfile.write(line)

    def build(self):
        print(f"Generating Python schema objects from {self.src} to {self.dst}")
        os.makedirs(self.dst, exist_ok=True)

        list_fns = ["schemas/arena-schema-files.json", "schemas/arena-schema-files-nonpersist.json"]

        obj_schemas = {}
        obj_classes = {}
        attr_classes = {}
        attr_schema = {}

        for list_fn in list_fns:
            obj_schema_path = os.path.join(self.src, list_fn)
            if not os.path.exists(obj_schema_path): continue
            with open(obj_schema_path) as tfile:
                obj_schemas.update(json.load(tfile))

            for _, obj_schema in obj_schemas.items():
                fn = obj_schema["file"]
                with open(os.path.join(self.src, fn)) as tfile:
                    schema = json.load(tfile)

                # resolve references locally via SchemaUpdater's pure functionality
                if "allOf" in schema:
                    new_schema = self.updater._parse_allof_ref(schema, expand_refs=True, attr_classes=attr_classes, obj_attr_schema=attr_schema)
                    del schema["allOf"]
                else:
                    new_schema = schema

                if "data" in new_schema.get("properties", {}) and "allOf" in new_schema["properties"]["data"]:
                    new_schema["properties"]["data"] = self.updater._parse_allof_ref(
                        new_schema["properties"]["data"], expand_refs=False, attr_classes=attr_classes, obj_attr_schema=attr_schema
                    )
                    del new_schema["properties"]["data"]["allOf"]

                if "data" not in new_schema.get("properties", {}) or "properties" not in new_schema["properties"]["data"]:
                    continue
                if "object_type" not in new_schema["properties"]["data"]["properties"]:
                    continue

                for object_type in new_schema["properties"]["data"]["properties"]["object_type"]["enum"]:
                    new_schema["properties"]["data"]["description"] = new_schema.get("description", "")
                    self._write_py_class(new_schema["properties"]["data"], object_type, "objects", self.dst, attr_classes, obj_classes)

        # export attribute classes
        for prop in attr_schema:
            if "type" in attr_schema[prop] and attr_schema[prop]["type"] == "object":
                self._write_py_class(attr_schema[prop], prop, "attributes", self.dst, attr_classes, obj_classes)

        data_schema = {
            "description": "Wraps all attributes in JSON.",
            "properties": collections.OrderedDict(sorted(attr_schema.items()))
        }
        self._write_py_class(data_schema, "data", "attributes", self.dst, attr_classes, obj_classes)

        # translation map
        with open("templates/py_attributes_translate.j2") as tfile:
            t = jinja2.Template(tfile.read())
        py_path = os.path.join(self.dst, "attributes", "translate.py")
        print(f"->{py_path}")
        with open(py_path, "w") as pfile:
            init_out = t.render(prop_schema=data_schema, snakecase=snakecase, pascalcase=pascalcase)
            pfile.write(f"{init_out}\n")

        # export inits
        obj_classes = collections.OrderedDict(sorted(obj_classes.items()))
        with open("templates/py_objects_init.j2") as tfile:
            t = jinja2.Template(tfile.read())
        py_path = os.path.join(self.dst, "objects", "__init__.py")
        print(f"->{py_path}")
        with open(py_path, "w") as pfile:
            pfile.write(f"{t.render(classes=obj_classes)}\n")

        attr_classes = collections.OrderedDict(sorted(attr_classes.items()))
        with open("templates/py_attributes_init.j2") as tfile:
            t = jinja2.Template(tfile.read())
        py_path = os.path.join(self.dst, "attributes", "__init__.py")
        print(f"->{py_path}")
        with open(py_path, "w") as pfile:
            pfile.write(f"{t.render(classes=attr_classes)}\n")
