"""
Created on 21 Apr 2023

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
    if len(sys.argv) != 4:
        print("USAGE: mivot-snippet-gen [class_name] [output_dir] [output_name]")
        print("   Create MIVOT snippets from VODML files")
        print("   :class_name: either a simple file or a class name")
        print("   :output_dir: path to the output directory")
        print("   :output_name: name of the output file")
        print("   exit status: 0 in case of success, 1 otherwise")
        sys.exit(1)

    if not os.path.isdir("../tmp_snippets"):
        os.makedirs("../tmp_snippets")

    xml_path = check_args(sys.argv[1])
    print(xml_path)

    time.sleep(1)

    snippet = ConcreteBuilder(xml_file=os.path.abspath(xml_path),
                              output_dir=os.path.abspath(sys.argv[2]),
                              output_name=sys.argv[3])
    snippet.build()
    snippet.outputResult()

    if os.path.isdir("../tmp_snippets"):
        os.system("rm -rf ../tmp_snippets")

def check_args(args):
    if os.path.exists(args):
        return args
    else:
        if not len(args.split(":")) == 2:
            print("Invalid format for class name")
            sys.exit(1)
        generic = Builder(args.split(":")[0], args.split(":")[1],
                          ConcreteBuilder.getModelXMLFromName(args.split(":")[0]),
                          os.path.abspath("../tmp_snippets/"))
        generic.build()
        return generic.outputname


if __name__ == '__main__':
    main()
