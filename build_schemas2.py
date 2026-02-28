#!/usr/bin/env python3
import argparse
import sys
from generators.base import BaseGenerator
from generators.update import SchemaUpdater
from generators.docs import MarkdownGenerator
from generators.jekyll import JekyllGenerator
from generators.py import PythonGenerator
from generators.dotnet import DotnetGenerator

def cmd_update(args):
    SchemaUpdater(src=args.src).build()

def cmd_docs(args):
    MarkdownGenerator().build()

def cmd_jekyll(args):
    JekyllGenerator(dst=args.dst).build()

def cmd_py(args):
    PythonGenerator(src=args.src, dst=args.dst).build()

def cmd_dotnet(args):
    DotnetGenerator(src=args.src, dst=args.dst).build()

def cmd_all(args):
    print("Running all sequentially...")
    SchemaUpdater(src=args.src).build()
    MarkdownGenerator().build()
    JekyllGenerator(dst=args.jekyll_dst).build()
    PythonGenerator(src=args.src, dst=args.py_dst).build()
    DotnetGenerator(src=args.src, dst=args.dotnet_dst).build()

def main():
    parser = argparse.ArgumentParser(description="ARENA Schema Builder V2")
    subparsers = parser.add_subparsers(dest="command", help="commands", required=True)

    # 1. Update Subcommand
    parser_update = subparsers.add_parser("update", help="Update intermediate schemas")
    parser_update.add_argument("src", help="Source folder of schemas (e.g. from arena-web-core/build)")
    parser_update.set_defaults(func=cmd_update)

    # 2. Docs Subcommand
    parser_docs = subparsers.add_parser("docs", help="Generate Markdown documentation")
    parser_docs.set_defaults(func=cmd_docs)

    # 3. Jekyll Subcommand
    parser_jekyll = subparsers.add_parser("jekyll", help="Generate Jekyll site files")
    parser_jekyll.add_argument("dst", help="Destination folder for Jekyll markdown")
    parser_jekyll.set_defaults(func=cmd_jekyll)

    # 4. Py Subcommand
    parser_py = subparsers.add_parser("py", help="Generate Python classes")
    parser_py.add_argument("src", help="Source folder of schemas (e.g. from arena-web-core/build)")
    parser_py.add_argument("dst", help="Destination folder for Python code")
    parser_py.set_defaults(func=cmd_py)

    # 5. Dotnet Subcommand
    parser_dotnet = subparsers.add_parser("dotnet", help="Generate C#/.NET classes")
    parser_dotnet.add_argument("src", help="Source folder of schemas (e.g. from arena-web-core/build)")
    parser_dotnet.add_argument("dst", help="Destination folder for C# code")
    parser_dotnet.set_defaults(func=cmd_dotnet)

    # 6. All Subcommand
    parser_all = subparsers.add_parser("all", help="Run all generators sequentially")
    parser_all.add_argument("--src", required=True, help="Source folder of schemas")
    parser_all.add_argument("--jekyll-dst", required=True, help="Destination folder for Jekyll markdown")
    parser_all.add_argument("--py-dst", required=True, help="Destination folder for Python code")
    parser_all.add_argument("--dotnet-dst", required=True, help="Destination folder for C# code")
    parser_all.set_defaults(func=cmd_all)

    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()
