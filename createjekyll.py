import json
import os
import sys

input_folder = 'docs/'
obj_schema_path = 'schemas/arena-schema-files.json'
gp_sec_title = 'ARENA Objects'
sec_title = 'Objects Schema'
sec_nav_order = 8


def main():
    args = sys.argv[1:]
    print(args)
    if (len(args) == 0 or not os.path.isdir(args[0])):
        os.mkdir(args[0])

    output_folder = args[0]

    # make jekyll index.md with objects list
    md_lines = []
    md_lines.append('---\n')
    md_lines.append(f'title: {sec_title}\n')
    md_lines.append(f'nav_order: {sec_nav_order}\n')
    md_lines.append('layout: default\n')
    md_lines.append(f'parent: {gp_sec_title}\n')
    md_lines.append('has_children: true\n')
    md_lines.append('has_toc: false\n')
    md_lines.append('---\n')
    md_lines.append('\n')
    md_lines.append('# ARENA Message Objects\n')
    md_lines.append('\n')
    md_lines.append('|Object Message|Description|\n')
    md_lines.append('| :--- | :--- |\n')

    with open(obj_schema_path, 'r') as json_file_all:
        files = json.load(json_file_all)
    for file in files:
        filename = os.path.basename(files[file]['file'])
        title = files[file]['title']
        desc = files[file]['description']
        md_lines.append(f'|[{title}]({filename[:-5]})|{desc}|\n')

    out = ''.join(md_lines)
    index_path = os.path.join(output_folder, 'index.md')
    print(f'-->{index_path}')
    f = open(index_path, 'w')
    f.write(out)
    f.close()

    # make jekyll.md for each object
    for filename in os.listdir(input_folder):
        with open(os.path.join(input_folder, filename), 'r') as f:
            text = f.read()
            lines = text.split('\n')
            md_lines = []
            md_lines.append('---\n')
            md_lines.append(f'title: {lines[0]}\n')
            md_lines.append('nav_order: 1\n')
            md_lines.append('layout: default\n')
            md_lines.append(f'parent: {sec_title}\n')
            md_lines.append(f'grand_parent: {gp_sec_title}\n')
            md_lines.append('---\n')
            md_lines.append('\n')
            md_lines.append(text)
            out = ''.join(md_lines)
            md_path = os.path.join(output_folder,  filename)
            print(f'-->{md_path}')
            f = open(os.path.join(output_folder, filename), 'w')
            f.write(out)
            f.close()


if __name__ == '__main__':
    main()
