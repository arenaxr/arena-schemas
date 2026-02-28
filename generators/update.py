import json
import os
from .base import BaseGenerator

class SchemaUpdater(BaseGenerator):
    """Flattens allOf and $ref to produce intermediate JSON."""

    def __init__(self, src, **kwargs):
        super().__init__(**kwargs)
        self.src = src
        self.output_folder = "schemas"
        self.list_fns = ["schemas/arena-schema-files.json", "schemas/arena-schema-files-nonpersist.json"]

    def _parse_allof_ref(self, allof_schema, expand_refs=True, attr_classes=None, obj_attr_schema=None):
        if attr_classes is None:
            attr_classes = {}
        if obj_attr_schema is None:
            obj_attr_schema = {}

        new_schema = allof_schema
        for props in allof_schema.get("allOf", []):
            for key in props:
                if key == "$ref":
                    ref = props[key].split("#")
                    key = ref[1].replace("/", "") if len(ref) > 1 else ref[0].split("/")[-1].replace(".json", "")

                    if not key:
                        key = ref[0].split("/")[-1].replace(".json", "")

                    with open(os.path.join(self.src, ref[0])) as f:
                        sub_schema = json.load(f)

                    if expand_refs:
                        props = sub_schema
                    else:
                        from caseconverter import pascalcase, snakecase
                        for prop in sub_schema.get("properties", {}):
                            attr_class = pascalcase(prop)
                            attr_ns = snakecase(prop)
                            obj_attr_schema[prop] = sub_schema["properties"][prop]
                            if "properties" in sub_schema["properties"][prop]:
                                attr_classes[attr_ns] = attr_class
                            else:
                                attr_classes[attr_ns] = None
                        continue

                if key not in new_schema:
                    new_schema[key] = {}
                new_schema[key].update(props[key])
        return new_schema

    def build(self):
        print(f"Updating intermediate schemas from {self.src} to {self.output_folder}/")
        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)

        obj_schemas = {}
        for list_fn in self.list_fns:
            obj_schema_path = os.path.join(self.src, list_fn)
            if not os.path.exists(obj_schema_path):
                print(f"Warning: {obj_schema_path} does not exist. Skipping.")
                continue

            with open(obj_schema_path) as f:
                obj_schemas.update(json.load(f))

            for _, obj_schema in obj_schemas.items():
                fn = obj_schema["file"]
                src_path = os.path.join(self.src, fn)
                with open(src_path) as f:
                    schema = json.load(f)

                if "allOf" in schema:
                    new_schema = self._parse_allof_ref(schema)
                    del schema["allOf"]
                else:
                    new_schema = schema

                if "data" in new_schema.get("properties", {}) and "allOf" in new_schema["properties"]["data"]:
                    new_schema["properties"]["data"] = self._parse_allof_ref(new_schema["properties"]["data"])
                    del new_schema["properties"]["data"]["allOf"]

                if "definitions" not in new_schema:
                    new_schema["definitions"] = {}

                if "data" in new_schema.get("properties", {}) and "properties" in new_schema["properties"]["data"]:
                    dprops = new_schema["properties"]["data"]["properties"]
                    for key in dprops:
                        if "type" in dprops[key] and dprops[key]["type"] == "object" and "deprecated" not in dprops[key]:
                            if key not in new_schema["definitions"]:
                                new_schema["definitions"][key] = dprops[key]
                                new_schema["properties"]["data"]["properties"][key] = {"$ref": f"#/definitions/{key}"}

                out_path = os.path.join(self.output_folder, os.path.basename(fn))
                with open(out_path, "w") as f:
                    json.dump(new_schema, f, indent=4)

        out_list_path = os.path.join(self.output_folder, "arena-schema-files.json")
        with open(out_list_path, "w") as f:
            json.dump(obj_schemas, f, indent=4)
