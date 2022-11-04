# mivot-validator

Python package for validating VOTables annotated with [MIVOT](https://github.com/ivoa-std/ModelInstanceInVot)

The validation process is 2 steps;
- VOTable validation (against 1.3)
- MIVOT validation

Both must succeed for the file to be considered as valid

The validator can process either individual files or directory contents (no recursivity)

## Installation

The validator is distributed as a Python package.
It won't be published in the PIP repo while MIVOT is not a standard.

```bash
BossMacBookPro$ pip3 install --force-reinstall git+https://github.com/ivoa/mivot-validator.git#egg=mivot-validator
```

## Usage

### Let's play with the unit-test sample

```bash
BossMacBookPro$ ls mivot-validator/tests/data/
test_instance_ko_1.xml	test_instance_ok_1.xml
cd mivot-validator/
pytest tests
```

### Commands

Validate an annotated VOTable
```bash
 mivot-votable-validate  <VOTable path>
```

Validate an XML file containing just a MAPPING block

```bash
 mivot-mapping-validate  <XML path>
```
## Examples taken out the unit test suite
### Check the VOTable tagged as valid

```bash
BossMacBookPro$ ls mivot-validator/tests/data/
test_instance_ko_1.xml	test_instance_ok_1.xml
BossMacBookPro$ mivot-votable-validate  mivot-validator/tests/data/test_instance_ok_1.xml 
   INFO - [__init__.py:  7 -   <module>()] - mivot_validator package intialized
   INFO - [schemas.py:1228 - include_schema()] - Resource 'XMLSchema.xsd' is already loaded
   INFO - [xml_validator.py: 17 -   __init__()] - Using schema http://www.ivoa.net/xml/VOTable/v1.3
   INFO - [xml_validator.py: 17 -   __init__()] - Using schema https://raw.githubusercontent.com/ivoa-std/ModelInstanceInVot/master/schema/xsd/mivot-v1.0.xsd
   INFO - [annotated_votable_validator.py: 76 - __validate_file()] - Validate file test_instance_ok_1.xml
   INFO - [annotated_votable_validator.py: 77 - __validate_file()] - - Validate against VOTable/v1.3
   INFO - [annotated_votable_validator.py: 83 - __validate_file()] - - passed
   INFO - [annotated_votable_validator.py: 85 - __validate_file()] - - Validate against MIVOT
   INFO - [annotated_votable_validator.py: 90 - __validate_file()] - test_instance_ok_1.xml is a valid annotated VOTable
```

### Check the file tagged as not valid

```bash
laurentmichel$ mivot-votable-validate  mivot-validator/tests/data/test_instance_ko_1.xml 
   INFO - [__init__.py:  7 -   <module>()] - mivot_validator package intialized
   INFO - [schemas.py:1228 - include_schema()] - Resource 'XMLSchema.xsd' is already loaded
   INFO - [xml_validator.py: 17 -   __init__()] - Using schema http://www.ivoa.net/xml/VOTable/v1.3
   INFO - [xml_validator.py: 17 -   __init__()] - Using schema https://raw.githubusercontent.com/ivoa-std/ModelInstanceInVot/master/schema/xsd/mivot-v1.0.xsd
   INFO - [annotated_votable_validator.py: 76 - __validate_file()] - Validate file test_instance_ko_1.xml
   INFO - [annotated_votable_validator.py: 77 - __validate_file()] - - Validate against VOTable/v1.3
   INFO - [annotated_votable_validator.py: 83 - __validate_file()] - - passed
   INFO - [annotated_votable_validator.py: 85 - __validate_file()] - - Validate against MIVOT
  ERROR - [xml_validator.py: 30 - validate_file()] - validation failed failed validating <Element '{http://www.ivoa.net/xml/merged-syntax}GLOBALS' at 0x7fec18998630> with XsdAssert(test='count (dm-mapping:INSTANCE[@dmrole !=...'):

Reason: assertion test if false

Schema:

  <xs:assert xmlns:xs="http://www.w3.org/2001/XMLSchema" test="count (dm-mapping:INSTANCE[@dmrole != '']) eq 0" />

Instance:

  <default:GLOBALS xmlns:default="http://www.ivoa.net/xml/merged-syntax">
      <default:INSTANCE dmid="SpaceFrame_ICRS" dmtype="coords:SpaceFrame">
          <default:INSTANCE dmrole="coords:SpaceFrame.refPosition" dmtype="coords:StdRefLocation">
              <default:ATTRIBUTE_XXX dmrole="coords:StdRefLocation.position" dmtype="ivoa:string" value="NoSet" />
          </default:INSTANCE>
          <default:ATTRIBUTE dmrole="coords:SpaceFrame.spaceRefFrame" dmtype="ivoa:string" value="ICRS" />
          <default:ATTRIBUTE dmrole="coords:SpaceFrame.equinox" dmtype="coords:Epoch" value="NoSet" />
      </default:INSTANCE>

      <default:INSTANCE dmrole="root" dmtype="test.model">
          <default:INSTANCE dmrole="test.header" dmtype="test.Header">
              <default:REFERENCE dmrole="test.frame" dmref="SpaceFrame_ICRS" />
              <default:INSTANCE dmrole="test.owner" dmtype="test.Owner">
                  <default:ATTRIBUTE dmrole="test.owner.name" dmtype="string" value="Michel" />
                  <default:ATTRIBUTE dmrole="test.owner.firstname" dmtype="string" value="Laurent" />
                  <default:ATTRIBUTE dmrole="test.title" dmtype="string" ref="_title" />
              </default:INSTANCE>
              <default:COLLECTION dmrole="test.points">
                  <default:JOIN sourceref="Results" />
              </default:COLLECTION>
      ...
      ...
  </default:GLOBALS>

Path: /VOTABLE/RESOURCE/RESOURCE[1]/default:VODML/default:GLOBALS

  ERROR - [annotated_votable_validator.py: 88 - __validate_file()] - MIVOT annotations are not valid

```
