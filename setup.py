from setuptools import setup

setup(
    name='mivot-validator',
    url='https://github.com/ivoa/mivot-validator',
    author='Laurent Michel',
    author_email='laurent.michel@astro.unistra.fr',
    packages=find_packages(),
    install_requires=['xmlschema'],
    version='1.0',
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

)

