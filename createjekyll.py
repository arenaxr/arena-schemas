import json
import os
import sys

output_folder = ''
input_folder = 'docs/'
obj_schema_path = 'schemas/arena-schema-files.json'


def main():
    global input_folder, obj_schema_path
    args = sys.argv[1:]
    print(args)
    if (len(args) == 0 or not os.path.isdir(args[0])):
        os.mkdir(args[0])

    output_folder = args[0]
    sec_title = 'Message Schema'

    # make jekyll index.md with objects list
    md_lines = []
    md_lines.append('---\n')
    md_lines.append(f'title: {sec_title}\n')
    md_lines.append('nav_order: 9\n')
    md_lines.append('layout: default\n')
    md_lines.append('has_children: true\n')
    md_lines.append('---\n')
    md_lines.append('\n')
    md_lines.append('# ARENA Message Objects\n')

    with open(obj_schema_path, 'r') as json_file_all:
        files = json.load(json_file_all)
    for file in files:
        print(files[file])
        fn = os.path.basename(files[file]['file'])
        t = files[file]['title']
        md_lines.append(f'- [{t}]({fn[:-5]})\n')

    out = ''.join(md_lines)
    print(out)
    f = open(os.path.join(output_folder, 'index.md'), 'w')
    f.write(out)
    f.close()

    # make jekyll.md for each object
    for filename in os.listdir(input_folder):
        with open(os.path.join(input_folder, filename), 'r') as f:
            text = f.read()
            lines = text.split('\n')
            print(text)
            md_lines = []
            md_lines.append('---\n')
            md_lines.append(f'title: {lines[0]}\n')
            md_lines.append('nav_order: 1\n')
            md_lines.append('layout: default\n')
            md_lines.append(f'parent: {sec_title}\n')
            md_lines.append('---\n')
            md_lines.append('\n')
            md_lines.append(text)
            out = ''.join(md_lines)
            print(out)
            f = open(os.path.join(output_folder, filename), 'w')
            f.write(out)
            f.close()

if __name__ == '__main__':
    main()
