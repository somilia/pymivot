"""
Created on 19 Apr 2023

@author: julien abid
"""
import os
import sys

from urllib.parse import urlparse
from urllib.request import urlretrieve

from mivot_validator.instance_checking.generic_snippet_builder import ExtendedBuilder


def main():
    """
    Package launcher (script)
    """
    if len(sys.argv) != 2:
        print("USAGE: mivot-snippet-gen [path]")
        print("   Create MIVOT snippets from VODML files")
        print("   path: either a simple file or an url")
        print("   exit status: 0 in case of success, 1 otherwise")
        sys.exit(1)

    path = check_args(sys.argv[1])

    snippet = ExtendedBuilder(vodml_path=path)
    if snippet.build():
        print("\n===============================================")
        print(f"Snippets generated in {os.path.abspath(os.getcwd() + '/../tmp_snippets/')} \nin the folder : "
              f"{os.path.basename(sys.argv[1]).split('.')[0].split('_')[0].split('-')[0].lower()}")
        print("===============================================\n")

        if os.path.isdir("tmp_vodml"):
            os.system("rm -rf tmp_vodml")

        sys.exit(0)


def check_args(args):
    """
    Check if the path is a file or an url and download the file if needed
    :args: path or link
    :return: local path
    """
    local_vodml_path = args
    if urlparse(args).scheme:
        # If vodml_path is an URL, download the file to a local temporary directory
        temp_dir = "tmp_vodml"
        os.makedirs(temp_dir, exist_ok=True)
        local_vodml_path = os.path.join(temp_dir, os.path.basename(args))
        urlretrieve(args, local_vodml_path)

    return local_vodml_path


if __name__ == '__main__':
    main()
