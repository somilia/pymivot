"""
Created on 21 Apr 2023

launcher script for the concrete snippet generator package

@author: julien abid
"""
import os.path
import sys
import time
from mivot_validator.instance_checking.concrete_snippet_builder import ConcreteBuilder
from mivot_validator.instance_checking.snippet_builder import Builder

def main():
    """
    Package launcher (script)
    """
    if 4 > len(sys.argv) > 5:
        print("USAGE: mivot-snippet-gen [class_name] [output_dir] [output_name] <classes_list>")
        print("   Create MIVOT snippets from VODML files")
        print("   :class_name: either a absolute file path to any MIVOT mapping class or just a class name as model:Class")
        print("   :output_dir: path to the choosen output directory")
        print("   :output_name: name of the output file (no need to put the extension at the end of it)")
        print("   :classes_list: [OPTIONAL] list of classes to be included in the snippet, it will prevent the script to "
              "ask for the user input if given.")
        print("   exit status: 0 in case of success, 1 otherwise")
        sys.exit(1)

    if not os.path.isdir("../tmp_snippets"):
        os.makedirs("../tmp_snippets")

    xml_path = check_args(sys.argv[1], 0)
    classes_list = check_args(sys.argv[4] if len(sys.argv) == 5 else None, 1)
    print(classes_list)

    time.sleep(1)

    snippet = ConcreteBuilder(xml_file=os.path.abspath(xml_path),
                              output_dir=os.path.abspath(sys.argv[2]),
                              output_name=sys.argv[3],
                              concrete_list=classes_list)
    snippet.build()
    snippet.outputResult()

def check_args(args, type):
    if args is None:
        return
    elif type == 0:
        if os.path.exists(args):
            return args

        if not len(args.split(":")) == 2:
            print("Invalid format for class name")
            sys.exit(1)
        generic = Builder(args.split(":")[0], args.split(":")[1],
                          ConcreteBuilder.getModelXMLFromName(args.split(":")[0]),
                          os.path.abspath("../tmp_snippets/"))
        generic.build()
        return generic.outputname
    elif type == 1:
        if not args.__contains__('[') and args.__contains__(']'):
            print("Invalid format for classes list")
            sys.exit(1)
        return args[1:-1].split(',')

if __name__ == '__main__':
    main()
