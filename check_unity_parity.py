import os
import re
import glob
import sys

from build_schemas4 import SchemaLoader

def main():
    loader = SchemaLoader('schemas')
    loader.build_models()
    print(f"Loaded {len(loader.arena_objects)} ARENA Objects and {len(loader.components)} Components.")

    unity_dir = '../arena-unity/Runtime/Components'
    unity_files = glob.glob(os.path.join(unity_dir, '*.cs'))

    # Dictionary mapping schema_name -> set(properties in comments)
    unity_components = {}
    unity_file_map = {}

    for f in unity_files:
        with open(f, 'r') as file:
            content = file.read()

            # Find the component name from the comment
            # e.g., // ARENA box component unity conversion status:
            match = re.search(r'// ARENA ([a-zA-Z0-9_\-]+) component unity conversion status:', content)
            if not match:
                continue

            schema_name = match.group(1)
            unity_file_map[schema_name] = os.path.basename(f)

            props = set()
            # Find all TODO, DONE, and N/A properties
            for line in content.split('\n'):
                line = line.strip()

                # Stop parsing properties once we hit the json variable declaration
                if line.startswith("public Arena") and "Json json =" in line:
                    break

                # Include N/A, DONE, and TODO. Also allow hyphens in property names (e.g. ar-hit-test)
                m = re.match(r'//\s*(?:TODO|DONE|N\/A):\s*([a-zA-Z0-9_\-]+)', line)
                if m:
                    props.add(m.group(1))

            unity_components[schema_name] = props

    print("\n--- IDENTIFYING MISSING OR EXTRA PROPERTIES ---")

    # Combine wire objects and lesser components for checking
    all_schemas = {}
    all_schemas.update(loader.arena_objects)
    all_schemas.update(loader.components)

    missing_in_unity_files = []
    deprecated_but_in_unity = []

    for name, schema in all_schemas.items():
        if name not in unity_components:
            missing_in_unity_files.append(name)
            continue

        # Schema objects don't have a direct 'deprecated' flag currently
        # properties do: schema.properties['propName'].deprecated
        # Use inline properties for Wire Objects, otherwise all properties for true components
        if not schema.is_component:
            # For wire objects, we ONLY want top-level properties.
            # We look at the actual properties defined in the schema,
            # and explicitly exclude any property that is a component reference.
            schema_props = set()
            for prop_name, prop in schema.properties.items():
                if not prop.is_ref:  # If it's not a component reference, it's a true top-level wire property
                    schema_props.add(prop_name)
        else:
            schema_props = set(schema.properties.keys())

        if "object_type" in schema_props: schema_props.remove("object_type")

        unity_props = unity_components[name]

        missing_in_comments = schema_props - unity_props
        extra_in_comments = unity_props - schema_props

        # if missing_in_comments or extra_in_comments:
        #     filename = unity_file_map[name]
        #     print(f"\n[{filename}] ({name})")
        #     if missing_in_comments:
        #         print(f"  Missing in comments (added to schema?): {missing_in_comments}")
        #     if extra_in_comments:
        #         print(f"  Extra in comments (removed from schema?): {extra_in_comments}")

    print(f"\n--- MISSING UNITY STUBS ({len(missing_in_unity_files)}) ---")
    for name in sorted(missing_in_unity_files):
        print(f"  {name}")

    print(f"\n--- DEPRECATED BUT IN UNITY ({len(deprecated_but_in_unity)}) ---")
    for name in sorted(deprecated_but_in_unity):
        print(f"  {name}")

if __name__ == '__main__':
    main()
