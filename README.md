# Introduction
This Python package contains two key utilities designed to abstract the names of entries in EMDB, EMPIAR and the upcoming segmentation (image annotation) archive. They are: 
* **classes** that represent entry names, and 
* **compiled regular expressions** to parse entry names.

The classes rely on the compiled regular expressions so that the supported behaviours are consistent.

## Classes
There are two main classes:
* `ImageName` represents EMDB/EMPIAR image accessions or file names, which are viewable in the Volume Browser;
* `AnnotationName` represents EMDB/EMPIAR image annotation accessions or file names.

The classes are designed to handle names having any one of the following forms: 
* `'emd_1234'`
* `'EMD-1234.map'`
* `'EMD_1234.mrc'`
* `'emd-1234.rec'`
* `'emd_1234-v0.8.1.dev3.map'`
* `'empiar_10311-20140801_hela-wt_xy5z8nm_as-template_match_aligned_binned_4.mrc'`
* `'emd_1234-v0.8.1.dev9-0HCyC5f.sff'` (image annotation with valid annotation accession)

## Compiled Regular Expressions
A compiled regular expression is a [`re.Pattern`](https://docs.python.org/3/library/re.html#regular-expression-objects) object with [a particular API](https://docs.python.org/3/library/re.html#regular-expression-objects). This package has two compiled regular expressions:
* `IMAGE_NAME_CRE` and 
* `ANNOTATION_NAME_CRE`

each corresponding to the two classes.

## Quick Start
1. Install the package

```shell
pip install git+https://github.com/emdb-empiar/names.git
```

2. Import and use the classes for archive entry or file names. Reference the required attributes. See the section on Attributes below.

```python
from names import ImageName, AnnotationName, IMAGE_NAME_CRE, ANNOTATION_NAME_CRE

# EMDB image
emdb_name = 'emd_1234.map'
image_name = ImageName(emdb_name)
print(image_name.canonical_name)  # emd_1234
print(image_name.uppercase_hyphen_name)  # EMD-1234
print(image_name.ext)  # map

# using IMAGE_NAME_CRE
image_name_match = IMAGE_NAME_CRE.match(emdb_name)
print(image_name_match.group('prefix'))  # emd
print(image_name_match.group('entry_id'))  # 1234
print(image_name_match.group('suffix'))  # ''
print(image_name_match.group('ext'))  # map

# EMPIAR image
empiar_name = 'empiar_10087_c2_tomo02.mrc'
image_name = ImageName(empiar_name)
print(image_name.canonical_name)  # empiar_10087_c2_tomo02
print(image_name.uppercase_hyphen_name)  # EMPIAR-10087
print(image_name.ext)  # mrc

# using IMAGE_NAME_CRE
image_name_match = IMAGE_NAME_CRE.match(empiar_name)
print(image_name_match.group('prefix'))  # empiar
print(image_name_match.group('entry_id'))  # 10087
print(image_name_match.group('suffix'))  # _c2_tomo02
print(image_name_match.group('ext'))  # mrc

# EMDB annotation
emdb_name = 'emd_1234-ZfizoG0.sff'
annot_name = AnnotationName(emdb_name)
print(annot_name.canonical_name)  # emd_1234
print(annot_name.annotation_name)  # emd_1234-ZfizoG0
print(annot_name.uppercase_hyphen_name)  # EMD-1234
print(annot_name.ext)  # sff
print(annot_name.noid)  # ZfizoG0
print(annot_name.is_valid())  # True

# using ANNOTATION_NAME_CRE
image_name_match = ANNOTATION_NAME_CRE.match(emdb_name)
print(image_name_match.group('prefix'))  # emd
print(image_name_match.group('entry_id'))  # 1234
print(image_name_match.group('suffix'))  # '-ZfizoG0'
print(image_name_match.group('ext'))  # sff

# EMPIAR annotation
empiar_name = 'empiar_10087_c2_tomo02-MJhbMT8.json'
annot_name = AnnotationName(empiar_name)
print(annot_name.canonical_name)  # empiar_10087_c2_tomo02
print(annot_name.annotation_name)  # empiar_10087_c2_tomo02-MJhbMT8
print(annot_name.uppercase_hyphen_name)  # EMPIAR-10087
print(annot_name.ext)  # json
print(annot_name.noid)  # MJhbMT8
print(annot_name.is_valid())  # True

# using ANNOTATION_NAME_CRE
image_name_match = ANNOTATION_NAME_CRE.match(empiar_name)
print(image_name_match.group('prefix'))  # empiar
print(image_name_match.group('entry_id'))  # 10087
print(image_name_match.group('suffix'))  # _c2_tomo02-MJhbMT8
print(image_name_match.group('ext'))  # json
```

## Classes in Detail
The following attributes are present in both `ImageName` and `AnnotationName` objects. We illustrate each attributes using the following names: `emd_1234.map`, `empiar_10753-lm44_2_sic1_018_ali1_binned_4.mrc`, `empiar_10753-lm44_2_sic1_018_ali1_binned_4-jsiLm2m.sff`.

> Note: All attributes default to `None` if the name is invalid unless otherwise specified.

* `prefix` either `'emd'` or `'empiar'` depending on the file name;
* `entry_id` the numerical identifier e.g. `1234` or `10753`;
* `ext` a sequent of letters indicating the format e.g. `map`, `mrc`, `sff`, `hff`, `json` etc.; defaults to `map` for EMDB, `mrc` for EMPIAR and `sff` for `AnnotationName` objects;
* `suffix` (if present in the name) any text between the `entry_id` and the extension e.g. `empiar_10753-lm44_2_sic1_018_ali1_binned_4` (for `ImageName`), `empiar_10753-lm44_2_sic1_018_ali1_binned_4-jsiLm2m` for `AnnotationName`)
* `canonical_name` uniquely identifies each image in the Volume Browser (VB), typicall consists of `prefix`, `entry_id` and `suffix` (if present) without any extension e.g. `emd_1234`, `empiar_10753-lm44_2_sic1_018_ali1_binned_4`; 
* `uppercase_hyphen_name` the accession with uppercase prefix, a hyphen ('-') and terminated with the numerical identifier e.g. `EMD-1234`, `EMPIAR-10753`
* `lowercase_hyphen_name` similar to the `uppercase_hyphen_name` but having the prefix in lowercase e.g. `emd-1234`, `empiar-10753`
* `uppercase_underscore_name` similar to the `uppercase_hyphen_name` but having '_' instead of '-' e.g.  `EMD_1234`, `EMPIAR_10753`
* `lowercase_underscore_name` similar to the `lowercase_hyphen_name` but having '_' instead of '-' e.g. `emd_1234`, `empiar_10753`
* `full_name_upper` `prefix`, hyphen with `suffix` in uppercase e.g. `EMD-1234`, `EMPIAR-10753-LM44_2_SIC1_018_ALI1_BINNED_4`
* `full_name_lower` `prefix`, underscore with `suffix` in lowercase e.g. `emd-1234`, `empiar_10753-lm44_2_sic1_018_ali1_binned_4`
* `file_name` the expected name e.g. `emd_1234.map`, `empiar_10753-lm44_2_sic1_018_ali1_binned_4v.mrc`, `empiar_10753-lm44_2_sic1_018_ali1_binned_4-jsiLm2m.sff`
* `entry_subtree` provides the directory sequence at which to find related resources e.g. `12/1234` and `empiar_10753/empiar_10753-lm44_2_sic1_018_ali1_binned_4` for corresponding image resources, `empiar_10753/empiar_10753-lm44_2_sic1_018_ali1_binned_4/jsiLm2m/` for annotation resources;

In addition to the above, `AnnotationName` objects also have the following attributes:
* `noid` nice opaque ID (NOID) consisting of a check-digit to catch transcription errors, which uniquely identifies each annotation; we use the Python `noid` package to generate and validate NOIDs e.g. `jsiLm2m` 
* `annotation_name` consists of `canonical_name`, hyphen the `noid` e.g. `empiar_10753-lm44_2_sic1_018_ali1_binned_4-jsiLm2m`
* `qualifier` - the extra name parameters used to distinguish EMPIAR volumes for the same entry e.g. `-lm44_2_sic1_018_ali1_binned_4` (including the first character - either '_' or '-')

`AnnotationName` objects also have the following method:
* `is_valid()` checks whether the noid is valid; returns a boolean


### Compiled Regular Expressions in Detail

The compiled regular expressions are case-insenstive and should be directly against strings to be matched. Both have four (4) groups present, which can be displayed using the `groupindex` attribute. 

```python
from names import IMAGE_NAME_CRE

print(IMAGE_NAME_CRE.groupindex)
# {'prefix': 2, 'entry_id': 4, 'suffix': 5, 'ext': 6}
```

These groups can then be used for valid matches to extract the parts of the name.

```python
from names import IMAGE_NAME_CRE

entry_name = "empiar_10753-lm44_2_sic1_018_ali1_binned_4.mrc"
match_obj = IMAGE_NAME_CRE.match(entry_name)
print(match_obj.group('prefix')) # empiar
# etc
```

> Tip: Feel free to use other attributes and methods as required e.g. `search()`


## Motivation
This package has arisen due to the need to have a single reference point on how to handle EMDB and EMPIAR accession and file names. The multiplicity of ways to denote entries results in unnecessariy complex code. By using this package, dependencies can use the attributes and methods it presents without the need to parse names.
* `oil`, the Volume Browser (VB) loader, enforces the use of canonical identifiers for each volume it may display; this package provides a uniform interface that all VB dependencies may use to refer to canonical identifiers.
* Annotation accessions have been designed to include a check digit check to catch simple transcription errors. This package handles validation of annotation names transparently.
* The paths where files are stored can also be handled transparently by referring to the `entry_subtree` attribute.
* A uniform set of attributes for various accession types e.g. `canonical_name`, `uppercase_hyphen_name` etc.
