# Introduction
This package contains classes and compiled regular expressions to abstract entry file names in EMDB, EMPIAR and the upcoming segmentation archive. There are two main classes:
* `ImageName` abstracts EMDB and EMPIAR image file names;
* `AnnotationName` abstracts files containing annotations (textual and geometrical).
There are three compiled regular expressions:
* `IMAGE_NAME_CRE`
* `ANNOTATION_NAME_CRE`, and
* `NOID_CRE`

## Motivation
EMDB and EMPIAR 3D volume accessions may be represented in various ways leading to unnecessarily complex code. In particular, Volume Browser (VB) enforces the use of canonical entry identifiers for each volume it may display. 
- Annotation accessions also include a CRC check to catch typos. This feature can be handled transparently by a dedicated package.
- The paths where files are stored can also be handled transparently.
- Regular expressions can be specified at a single place for all implementations. These may also be reused elsewhere for tests of filenames without the need to parse the contents. 
- A uniform set of attributes for various accession types e.g. `canonical_name`, `uppercase_hyphen_name` etc.

## Attributes
The following are the key attributes for each name object. We illustrate each for the an EMDB and EMPIAR entry.
* `canonical_name` - the unique image name used to identify the image in the volume browser (VB);
* `full_hyphen_upper` - 

In addition to the above, `AnnotationName` objects also have the following attributes:
* `annotation_name` - the image-annotation name consisting of the canonical image name as well as the annotation archive (`noid`);
* `noid` - the CRC-checking nice opaque ID (noid), which uniquely identifies each annotation;
* `qualifier` - the extra name parameters used to distinguish EMPIAR volumes for the same entry;

Usage
1. Install the package

```shell
pip install git+https://github.com/emdb-empiar/names.git
```

2. Import and use the classes agains archive entry names.
```python
from names import ImageName, AnnotationName

# emdb images
image_name = ImageName('emd_1234.map')
image_name.canonical_name # emd_1234
image_name.full_name_upper # EMD-1234
image_nmae.ext # map

# empiar images
image_name = ImageName('empiar_10087_c2_tomo02.mrc')
image_name.canon

```
