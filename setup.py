"""
Setup script for mivot-validator2
@author: Laurent Michel
"""

from setuptools import setup, find_packages

entry_points = {
    "console_scripts": [
        "mivot-votable-validate = pymivot.validator2.launchers.votable_launcher:main",
        "mivot-validate = pymivot.validator2.launchers.votable_launcher:main",
        "mivot-mapping-validate = pymivot.validator2.launchers.mivot_launcher:main",
        "types-and-roles-validate = pymivot.validator2.launchers.typesandroles_launcher:main",
        "mivot-instance-validate = pymivot.validator2.launchers.instance_checking_launcher:main",
        "mivot-snippet-model = pymivot.validator2.launchers.model_snippets_launcher:main",
        "mivot-snippet-instance = pymivot.validator2.launchers.instance_snippet_launcher:main",
    ]
}

with open("README.md", encoding="utf-8") as file:
    readme_file = file.read()


setup(
    name="mivot-validator2",
    url="https://github.com/ivoa/mivot-validator",
    author="Laurent Michel",
    author_email="laurent.michel@astro.unistra.fr",
    packages=find_packages(),
    install_requires=["xmlschema", "lxml"],
    include_package_data=True,
    version="2.0",
    license="MIT",
    description="Validator for model annotations in VOTable",
    long_description=readme_file,
    python_requires=">=3.6",
    classifiers=[
        "Topic :: Scientific/Engineering :: Astronomy",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: >=3.6",
    ],
    entry_points=entry_points,
)
