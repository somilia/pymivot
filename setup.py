"""
Setup script for mivot-validator
@author: Laurent Michel
"""

from setuptools import setup, find_packages

entry_points = {
    "console_scripts": [
        "mivot-votable-validate = mivot_validator.launchers.votable_launcher:main",
        "mivot-validate = mivot_validator.launchers.votable_launcher:main",
        "mivot-mapping-validate = mivot_validator.launchers.mivot_launcher:main",
        "types-and-roles-validate = mivot_validator.launchers.typesandroles_launcher:main",
        "mivot-instance-validate = mivot_validator.launchers.instance_checking_launcher:main",
        "mivot-snippet-model = mivot_validator.launchers.model_snippets_launcher:main",
        "mivot-snippet-instance = mivot_validator.launchers.instance_snippet_launcher:main",
    ]
}

with open("README.md", encoding="utf-8") as file:
    readme_file = file.read()


setup(
    name="mivot-validator",
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
