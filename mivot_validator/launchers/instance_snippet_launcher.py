"""
Created on 21 Apr 2023

launcher script for the instance snippet generator package

@author: julien abid
"""
import os.path
import sys
import argparse
from mivot_validator.instance_checking.instance_snippet_builder import InstanceBuilder
from mivot_validator.instance_checking.snippet_builder import Builder

CONSTRAINTS = None


def main():
    """
    Package launcher (script)
    """

    parser = argparse.ArgumentParser(
        description="Create MIVOT snippets from VODML files"
    )
    parser.add_argument(
        "class_name",
        metavar="class_name",
        type=str,
        nargs="?",
        help="either a absolute file path to any MIVOT mapping class"
        " or just a class name as model:Class",
    )
    parser.add_argument(
        "output_dir",
        metavar="output_dir",
        type=str,
        nargs="?",
        help="path to the choosen output directory",
    )
    parser.add_argument(
        "output_name",
        metavar="output_name",
        type=str,
        nargs="?",
        help="name of the output file (no need to put the extension at the end of it)",
    )
    parser.add_argument(
        "-cc",
        "--concrete-class",
        metavar="classes_list",
        type=lambda x: dict((i.split("=") for i in x.split(","))),
        nargs="?",
        action="append",
        help="[OPTIONAL] list of classes to be included in the snippet, "
        "it will prevent the script to ask for the user input if given.\n"
        "Syntax is : dmrole=model:Type.role,"
        "context=model:ParentType,dmtype=model:Type,class=model:Type",
    )

    args = vars(parser.parse_args())

    if args["output_dir"] is None or args["output_name"] is None or args["class_name"] is None:
        parser.print_help()
        sys.exit(1)

    if not os.path.isdir("../tmp_snippets"):
        os.makedirs("../tmp_snippets")

    xml_path = check_args(args["class_name"], 0, parser)
    classes_list = check_args(args["concrete_class"], 1, parser)

    snippet = InstanceBuilder(
        xml_file=os.path.abspath(xml_path),
        output_dir=os.path.abspath(args["output_dir"]),
        output_name=args["output_name"],
        concrete_list=classes_list,
    )
    snippet.build()
    snippet.output_result()


def check_args(args, mode, parser=None):
    """
    Check arguments validity
    :args: arguments
    :mode: type of arguments
    :return: arguments
    """
    if args is None:
        return None
    if mode == 0:
        if os.path.exists(args):
            return args

        if not len(args.split(":")) == 2:
            print("Invalid format for class name")
            sys.exit(1)
        generic = Builder(
            args.split(":")[0],
            args.split(":")[1],
            InstanceBuilder.get_model_xml_from_name(args.split(":")[0]),
            os.path.abspath("../tmp_snippets/"),
        )
        generic.build()
        return generic.outputname
    if mode == 1:
        for my_dict in args:
            if not all(
                x in my_dict.keys() for x in ["dmtype", "dmrole", "context", "class"]
            ):
                print("Invalid format for class name")
                if parser is not None:
                    parser.print_help()
                sys.exit(1)
        return args
    return None


if __name__ == "__main__":
    main()
