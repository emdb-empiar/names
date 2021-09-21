import re
import sys

import noid

"""
EMDB_CRE = re.compile(r'^(test-)*emd[-_](?P<entry_id>\d{4,5})\.*(map|mrc|tif|tiff)*(\.gz)*$', re.IGNORECASE)
EMPIAR_CRE = re.compile(
    r'^(test-)*(?P<entry_id>^empiar[-_]\d{5})(?P<qualifier>[_.\-\w]*?)\.*(map|mrc|tif|tiff)*(\.gz)*$',
    re.IGNORECASE
)
"""

IMAGE_NAME_CRE = re.compile(
    r"^(?P<archive>(empiar|emp|EMP|EMPIAR|emd|emdb|EMD|EMDB))[-_](?P<id>\d{4,5})(?P<tail>[-_.\w]+)*([?].*)*$",
    re.IGNORECASE
)

ANNOTATION_NAME_CRE = re.compile(
    r'^(test-)*(?P<archive>(emd|empiar))[-_](?P<entry_id>\d{4,5})(?P<suffix>.*?)\.*(?P<ext>'
    r'(sff|hff|json|xml|h5|hdf5))*$',
    re.IGNORECASE)

NOID_CRE = re.compile(r'(?P<qualifier>.*)-(?P<noid>\w{7})$')


class ImageName:
    """Parse entry image names i.e. EMDB and EMPIAR images"""

    def __init__(self, given_name):
        """"""
        match = IMAGE_NAME_CRE.match(given_name)
        self._given_name = given_name
        self.matched = False
        if match:
            self.matched = True
            mg = match.group
            if mg('archive').lower() in ['empiar', 'emp']:
                self.ext = "mrc"
                self.archive = 'empiar'
                self.canonical_name = f"{mg('archive').lower()}_{mg('id')}{mg('tail')}"
            else:
                self.ext = "map"
                self.archive = 'emdb'
                self.canonical_name = f"{mg('archive').lower()}_{mg('id')}"
            self.id_only = mg('id')
            self.uppercase_hyphen_name = f"{mg('archive').upper()}-{mg('id')}"
            self.uppercase_underscore_name = f"{mg('archive').upper()}_{mg('id')}"
            self.lowercase_hyphen_name = f"{mg('archive').lower()}-{mg('id')}"
            self.lowercase_underscore_name = f"{mg('archive').lower()}_{mg('id')}"
            self.full_name_upper = f"{self._given_name.upper()}"
            self.full_name_lower = f"{self._given_name.lower()}"
            self.file_name = f"{self._given_name}.{self.ext}"

    def _eval(self):
        pass

    @property
    def entry_subtree(self):
        return


class AnnotationName:
    """An AnnotationName has the following structure:

    (test-)*(archive)[-_](entry_id)(suffix)(ext)*

    The suffix is further divided into:

    (qualifier)*(noid)

    An `AnnotationName` object takes a correctly-named segmentation file and extracts a lot of information
    about its identity as well as how it should be processed.

    Segmentation File Names
    -----------------------
    A correctly-named segmentation file has the following form: emd_DDDD[D]-AAAAAAA.<ext>, where

    - D is a numerical character, [D] refers to an optional character,
    - A is an alphanumeric character which constitutes the 7-digit segmentation accession.

    The segmentation accession (AAAAAAA) is designed to be self-checking and can only take
    on particular valid values i.e. it is not random or sequential and is generated using the Python `noid` package
    using the default template (-t/--template) and an empty scheme (-s/--scheme). For more information on working with
    noids please read the `noid` README.md documentation.

    Expected Behaviour of `AnnotationName` Objects
    ---------------------------------------------
    Consider the annotations with the given names 'emd_12345-3jisfj9.sff' and 'empiar_12345-some_var-ef3sk32.hff'; then if
    `annot_name = AnnotationName(given_name)` is an `AnnotationName` object:

    - `annot_name.archive` gives the archive as 'emdb' or 'empiar'
    - `annot_name.canonical_name` gives the canonical names without the segmentation accession i.e.
    'emd_12345', 'empiar_12345-some_var'
    - `annot_name.annotation_name` gives the annotation name (canonical name with segmentation accession i.e.
    'emd_12345-3jisfj9', 'empiar_12345-some_var-ef3sk32' without an extension
    - `annot_name.uppercase_hyphen_name` are 'EMD-12345', 'EMPIAR-12345'
    - `annot_name.lowercase_hyphen_name` are 'emd-12345', 'empiar-12345'
    - `annot_name.uppercase_underscore_name` are 'EMD_12345', 'EMPIAR_12345'
    - `annot_name.lowercase_underscore_name` are 'emd_12345', 'empiar_12345'
    - `annot_name.full_name_upper` are 'EMD_12345-3jisfj9', 'EMPIAR_12345-SOME_VAR-ef3sk32'
    - `annot_name.full_name_lower` are 'emd_12345-3jisfj9', 'empiar_12345-some_var-ef3sk32
    - `annot_name.file_name` are 'emd_12345-3jisfj9.sff', 'empiar_12345-some_var-ef3sk32.hff'
    - `annot_name.noid` are 'ejisfj9', 'ef3sk32'
    - `annot_name.ext` are 'sff', 'hff'
    - `annot_name.is_valid()` are True, False
    - `annot_name.entry_subtree` are '12/3/12345/ejisfj9/', 'empiar_12345/empiar_12345-some_var/ef3sk32/'


    """

    def __init__(self, given_name, verbose=False):
        self._given_name = given_name
        self._verbose = verbose
        # major parts (private attributes)
        self._test = False
        self.archive = None
        self.entry_id = None
        self.suffix = None
        self.ext = 'sff'
        self.qualifier = None
        self.noid = None
        # the attributes of interest
        self.canonical_name = None
        self.annotation_name = None
        self.uppercase_hyphen_name = None
        self.lowercase_hyphen_name = None
        self.uppercase_underscore_name = None
        self.lowercase_underscore_name = None
        self.full_name_upper = None
        self.full_name_lower = None
        self.file_name = None
        # match
        match = ANNOTATION_NAME_CRE.match(given_name)
        # evaluate the match
        self._eval(match)

    @property
    def is_test(self):
        return self._test

    def _eval(self, match):
        if match:
            if self._verbose:
                print(f"info: {match}", file=sys.stderr)
            if match.group(1):
                self._test = True
            self.entry_id = match.group('entry_id')
            self.suffix = match.group('suffix')
            suffix_match = NOID_CRE.match(self.suffix)
            if suffix_match:
                self.qualifier = suffix_match.group('qualifier')
                _noid = suffix_match.group('noid')
                self.noid = _noid
            else:
                self.qualifier = ''
                self.noid = '*******'  # invalid
            if match.group('archive').lower() == 'empiar':
                self._archive = match.group('archive')
                self.archive = 'empiar'
                self.canonical_name = f"{self._archive.lower()}_{self.entry_id}{self.qualifier}"
                self.annotation_name = f"{self.canonical_name}-{self.noid}"
            else:
                self._archive = match.group('archive')
                self.archive = 'emdb'
                self.canonical_name = f"{self._archive.lower()}_{self.entry_id}"
                self.annotation_name = f"{self.canonical_name}-{self.noid}"
            self.uppercase_hyphen_name = f"{self._archive.upper()}-{self.entry_id}"
            self.uppercase_underscore_name = f"{self._archive.upper()}_{self.entry_id}"
            self.lowercase_hyphen_name = f"{self._archive.lower()}-{self.entry_id}"
            self.lowercase_underscore_name = f"{self._archive.lower()}_{self.entry_id}"
            self.full_name_upper = f"{self._archive.upper()}-{self.entry_id}-{self.noid}"
            self.full_name_lower = f"{self._archive.lower()}-{self.entry_id}-{self.noid}"
            ext = match.group('ext')
            if ext is None:
                ext = "sff"
            if self._given_name.endswith(ext):
                self.file_name = self._given_name
            else:
                self.file_name = f"{self._given_name}.{ext}"
            self.ext = ext
        else:
            if self._verbose:
                print(f"error: failed to match '{self._given_name}'", file=sys.stderr)

    def is_valid(self):
        """Validate the noid"""
        return noid.validate(self.noid)

    @property
    def entry_subtree(self):
        subtree = ''
        if self.archive == 'emdb':
            if len(self.entry_id) == 4:
                subtree = f"{self.entry_id[:2]}/{self.entry_id}/{self.noid}/"
            elif len(self.entry_id) == 5:
                subtree = f"{self.entry_id[:2]}/{self.entry_id[2]}/{self.entry_id}/{self.noid}/"
            else:
                raise ValueError(f"entry {self._given_name} has invalid number of digits in name")
        elif self.archive == 'empiar':
            subtree = f"{self.lowercase_underscore_name}/{self.canonical_name}/{self.noid}/"
        return subtree

    def __str__(self):
        return self._given_name
