from setuptools import setup, find_packages

entry_points = {
    "console_scripts": [
        "mivot-votable-validate = mivot_validator.launchers.votable_launcher:main",
        "mivot-validate = mivot_validator.launchers.votable_launcher:main",
        "mivot-mapping-validate = mivot_validator.launchers.mivot_launcher:main",
        "types-and-roles-validate = mivot_validator.launchers.typesandroles_launcher:main",
        "mivot-instance-validate = mivot_validator.launchers.instance_checking_launcher:main",
        "mivot-snippet-generic = mivot_validator.launchers.generic_snippet_launcher:main"
    ]
}

setup(
    name='mivot-validator',
    url='https://github.com/ivoa/mivot-validator',
    author='Laurent Michel',
    author_email='laurent.michel@astro.unistra.fr',
    packages=find_packages(),
    install_requires=['xmlschema', 'lxml'],
    version='2.0',
    license='MIT',
    description='Validator for model annotations in VOTable',
    long_description=open('README.md').read(),
    python_requires=">=3.6",
    classifiers=[
        "Topic :: Scientific/Engineering :: Astronomy",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: >=3.6",
    ],
    entry_points=entry_points
)
