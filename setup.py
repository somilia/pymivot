from setuptools import setup

setup(
    name='mivot-validator',
    url='https://github.com/ivoa/mivot-validator',
    author='Laurent Michel',
    author_email='laurent.michel@astro.unistra.fr',
    packages=['measure'],
    install_requires=['xmlschema'],
    version='1.0',
    license='MIT',
    description='Validator for model annotations in VOTable',
    long_description=open('README.md').read(),
)

