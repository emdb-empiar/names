import re
import sys
import warnings

import noid

"""
EMDB_CRE = re.compile(r'^(test-)*emd[-_](?P<entry_id>\d{4,5})\.*(map|mrc|tif|tiff)*(\.gz)*$', re.IGNORECASE)
EMPIAR_CRE = re.compile(
    r'^(test-)*(?P<entry_id>^empiar[-_]\d{5})(?P<qualifier>[_.\-\w]*?)\.*(map|mrc|tif|tiff)*(\.gz)*$',
    re.IGNORECASE
)
"""

# image names are a bit more promiscuous than annotation names
IMAGE_NAME_CRE = re.compile(
    r"^(test-)*(?P<prefix>(empiar|emp|emd|emdb))[-_](?P<entry_id>\d{4,5})(?P<suffix>.*?)\.*"
    r"(?P<ext>(map|mrc|rec|st)(\.gz)*)*$",
    re.IGNORECASE
)

ANNOTATION_NAME_CRE = re.compile(
    r'^(test-)*(?P<prefix>(emd|empiar))[-_](?P<entry_id>\d{4,5})(?P<suffix>.*?)\.*(?P<ext>'
    r'(sff|hff|json|xml|h5|hdf5))*$',
    re.IGNORECASE)

# For annotations the suffix contains the qualifier and the noid (nice opaque ID)
_NOID_CRE = re.compile(r'(?P<qualifier>.*)-(?P<noid>\w{7})$')


class Name:
    ext = None
    CRE = None

    def __init__(self, given_name, verbose=False):
        """"""
        self._given_name = given_name
        self._verbose = verbose
        # private attrs
        self._test = False
        self.archive = None
        self.prefix = None
        self.entry_id = None
        self.suffix = None
        # the attributes of interest
        self.canonical_name = None
        self.uppercase_hyphen_name = None
        self.lowercase_hyphen_name = None
        self.uppercase_underscore_name = None
        self.lowercase_underscore_name = None
        self.full_name_upper = None
        self.full_name_lower = None
        self.file_name = None
        # match
        self._match = self.CRE.match(given_name)
        self._eval()

    @property
    def matched(self):
        return bool(self._match)

    def _eval(self):
        raise NotImplementedError

    @property
    def entry_subtree(self):
        raise NotImplementedError

    @property
    def is_test(self):
        return self._test

    def __str__(self):
        return self._given_name


class ImageName(Name):
    """Parse entry image names i.e. EMDB and EMPIAR images"""
    ext = 'map'
    CRE = IMAGE_NAME_CRE

    def _eval(self):
        if self._match:
            if self._verbose:
                print(f"info: {self._match}", file=sys.stderr)
            mg = self._match.group
            if mg(1):
                self._test = True
            self.entry_id = mg('entry_id')
            self.suffix = mg('suffix')
            self.prefix = mg('prefix')
            self.ext = mg('ext')
            if self.prefix.lower() in ['empiar', 'emp']:
                if self.ext is None:
                    self.ext = "mrc"
                self.archive = 'empiar'
                self.canonical_name = f"{self.prefix.lower()}_{self.entry_id}{self.suffix}"
            else:
                if self.ext is None:
                    self.ext = "map"
                self.archive = 'emdb'
                self.canonical_name = f"{self.prefix.lower()}_{self.entry_id}"
            self.uppercase_hyphen_name = f"{self.prefix.upper()}-{self.entry_id}"
            self.uppercase_underscore_name = f"{self.prefix.upper()}_{self.entry_id}"
            self.lowercase_hyphen_name = f"{self.prefix.lower()}-{self.entry_id}"
            self.lowercase_underscore_name = f"{self.prefix.lower()}_{self.entry_id}"
            self.full_name_upper = f"{self.prefix.upper()}-{self.entry_id}{self.suffix.upper()}"
            self.full_name_lower = f"{self.prefix.lower()}-{self.entry_id}{self.suffix.lower()}"
            if self._given_name.endswith(self.ext):
                self.file_name = self._given_name
            else:
                self.file_name = f"{self._given_name}.{self.ext}"
        else:
            if self._verbose:
                print(f"error: failed to match '{self._given_name}'", file=sys.stderr)

    @property
    def id_only(self):
        warnings.warn("attribute 'id_only' will be deprecated", PendingDeprecationWarning)
        return self.entry_id

    @property
    def entry_subtree(self):
        subtree = ''
        if self.archive == 'emdb':
            if len(self.entry_id) == 4:
                subtree = f"{self.entry_id[:2]}/{self.entry_id}/"
            elif len(self.entry_id) == 5:
                subtree = f"{self.entry_id[:2]}/{self.entry_id[2]}/{self.entry_id}/"
            else:
                raise ValueError(f"entry {self._given_name} has invalid number of digits in name")
        elif self.archive == 'empiar':
            subtree = f"{self.lowercase_underscore_name}/{self.canonical_name}/"
        return subtree


class AnnotationName(Name):
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
    ext = 'sff'
    CRE = ANNOTATION_NAME_CRE

    def __init__(self, *args, **kwargs):
        self.annotation_name = None
        self.qualifier = None
        self.noid = None
        super().__init__(*args, **kwargs)

    def _eval(self):
        if self._match:
            if self._verbose:
                print(f"info: {self._match}", file=sys.stderr)
            mg = self._match.group
            if mg(1):
                self._test = True
            self.entry_id = mg('entry_id')
            self.suffix = mg('suffix')
            suffix_match = _NOID_CRE.match(self.suffix)
            if suffix_match:
                self.qualifier = suffix_match.group('qualifier')
                _noid = suffix_match.group('noid')
                self.noid = _noid
            else:
                self.qualifier = ''
                self.noid = '*******'  # invalid
            self.prefix = mg('prefix')
            if self.prefix.lower() == 'empiar':
                self.archive = 'empiar'
                self.canonical_name = f"{self.prefix.lower()}_{self.entry_id}{self.qualifier}"
                self.annotation_name = f"{self.canonical_name}-{self.noid}"
            else:
                self.archive = 'emdb'
                self.canonical_name = f"{self.prefix.lower()}_{self.entry_id}"
                self.annotation_name = f"{self.canonical_name}-{self.noid}"
            self.uppercase_hyphen_name = f"{self.prefix.upper()}-{self.entry_id}"
            self.uppercase_underscore_name = f"{self.prefix.upper()}_{self.entry_id}"
            self.lowercase_hyphen_name = f"{self.prefix.lower()}-{self.entry_id}"
            self.lowercase_underscore_name = f"{self.prefix.lower()}_{self.entry_id}"
            self.full_name_upper = f"{self.prefix.upper()}-{self.entry_id}{self.qualifier.upper()}-{self.noid}"
            self.full_name_lower = f"{self.prefix.lower()}-{self.entry_id}{self.qualifier.lower()}-{self.noid}"
            ext = mg('ext')
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

    def is_valid(self):
        """Validate the noid"""
        return noid.validate(self.noid)
