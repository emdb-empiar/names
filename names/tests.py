"""
Particular use cases:
oil
* get_image_dest(basename)
* get_entry_subtree(basename)
* _validate_prep_is_canonical(args)

segue
* all use cases added in form of test

emdb_django.empiar3d
* [DONE] image_ids = get_image_ids(config['data']['omero_db_string'], entry_name.lowercase_underscore_name,
                                  entry_name.ext)
* [DONE] api_url = config['urls']['emdb_rest_api']; r = requests.get(api_url + "all/" + entry_name.uppercase_hyphen_name, verify=False); fast_axis = r.json()[entry_name.uppercase_hyphen_name][0]["map"]["axis_order"]["fast"]
* [DONE] api_url = config['urls']['emdb_rest_api']; s = requests.get(api_url + "analysis/" + entry_name.uppercase_hyphen_name, verify=False); histogram = json.dumps(s.json()[entry_name.uppercase_hyphen_name][0]["density_distribution"])
* [DONE] image_ids = get_image_ids(config['data']['omero_db_string'], entry_name.full_name_lower, entry_name.ext)
* [DONE] api_url = config['urls']['empiar_rest_api']; r = requests.get(api_url + "all/" + entry_name.uppercase_hyphen_name); entry_info = r.json()[entry_name.uppercase_hyphen_name]
* [DONE] image_params = get_image_params(config['data']['omero_db_string'], entry_name.full_name_lower, entry_name.ext, image_ids['top'])
* [TO TEST] fname = '/nfs/public/rw/pdbe/mol2cell/data/histograms/' + entry_name.lowercase_hyphen_name + '.json';             with open(fname, 'rb') as hdata:
                data = json.load(hdata)
                xs, y = challenge_hist(data, image_params['contrast_max'], image_params['contrast_min'])
                histogram = \"""{"y": \""" + str(y) + \""", "x":\""" + str(xs) + \"""}\"""
* [DONE] entry_name = _EntryName(kwargs.get('entry_name')); data_from_db = self.get_data_from_db(entry_name); data = self.parse_data(entry_name, data_from_db)
* [TO TEST] json_filename = self.get_json_filename(**kwargs)
"""

import re
import unittest

import noid
import psycopg2
import requests

from . import ImageName, AnnotationName

_image_attrs = [
    'canonical_name',
    'uppercase_hyphen_name',
    'lowercase_hyphen_name',
    'uppercase_underscore_name',
    'lowercase_underscore_name',
    'full_name_upper',
    'full_name_lower',
    'file_name',
]


class TestImageName(unittest.TestCase):
    def test_emdb_defaults(self):
        """Test that we have some value when failed parsing"""
        en = ImageName('emd1234')
        self.assertFalse(en.matched)
        self.assertFalse(en.is_test)
        self.assertIsNone(en.archive)
        self.assertIsNone(en.entry_id)
        self.assertIsNone(en.suffix)
        self.assertEqual('map', en.ext)
        self.assertEqual('', en.entry_subtree)
        for attr in _image_attrs:
            self.assertIsNone(getattr(en, attr))
        # valid name
        en = ImageName('emd_1234.map', verbose=True)
        self.assertFalse(en.is_test)
        self.assertTrue(en.matched)
        self.assertEqual('emdb', en.archive)
        self.assertEqual('1234', en.entry_id)
        self.assertEqual('', en.suffix)
        self.assertEqual('map', en.ext)
        self.assertEqual('12/1234/', en.entry_subtree)
        # required attributes
        values = [
            'emd_1234',
            'EMD-1234',
            'emd-1234',
            'EMD_1234',
            'emd_1234',
            'EMD-1234',
            'emd-1234',
            'emd_1234.map'
        ]
        for i, attr in enumerate(_image_attrs):
            expected_value = values[i]
            value = getattr(en, attr)
            self.assertEqual(expected_value, value)
        # test file
        en = ImageName('test-emd_1234.map', verbose=True)
        self.assertTrue(en.is_test)
        # .gz file
        en = ImageName('emd_1234.map.gz', verbose=True)
        self.assertEqual('map.gz', en.ext)

    def test_empiar_defaults(self):
        """Test that we have some value when failed parsing"""
        en = ImageName('empiar12345-some.other_value')
        self.assertFalse(en.matched)
        self.assertFalse(en.is_test)
        self.assertIsNone(en.archive)
        self.assertIsNone(en.entry_id)
        self.assertIsNone(en.suffix)
        self.assertEqual('map', en.ext)
        self.assertEqual('', en.entry_subtree)
        for attr in _image_attrs:
            self.assertIsNone(getattr(en, attr))
        # valid name
        en = ImageName('empiar_12345-some.other_value.mrc', verbose=True)
        self.assertFalse(en.is_test)
        self.assertTrue(en.matched)
        self.assertEqual('empiar', en.archive)
        self.assertEqual('12345', en.entry_id)
        self.assertEqual('-some.other_value', en.suffix)
        self.assertEqual('mrc', en.ext)
        self.assertEqual('empiar_12345/empiar_12345-some.other_value/', en.entry_subtree)
        # required attributes
        values = [
            'empiar_12345-some.other_value',
            'EMPIAR-12345',
            'empiar-12345',
            'EMPIAR_12345',
            'empiar_12345',
            'EMPIAR-12345-SOME.OTHER_VALUE',
            'empiar-12345-some.other_value',
            'empiar_12345-some.other_value.mrc'
        ]
        for i, attr in enumerate(_image_attrs):
            expected_value = values[i]
            value = getattr(en, attr)
            self.assertEqual(expected_value, value)
        # test file
        en = ImageName('test-empiar_12345-some.other_value.mrc', verbose=True)
        self.assertTrue(en.is_test)

    def test_empiar(self):
        en = ImageName('empiar_10052-ring_1')
        self.assertEqual('empiar', en.archive)
        self.assertEqual('10052', en.id_only)
        self.assertEqual('empiar_10052-ring_1', en.canonical_name)  # different
        self.assertEqual('EMPIAR-10052', en.uppercase_hyphen_name)
        self.assertEqual('EMPIAR_10052', en.uppercase_underscore_name)
        self.assertEqual('empiar-10052', en.lowercase_hyphen_name)
        self.assertEqual('empiar_10052', en.lowercase_underscore_name)
        self.assertEqual('EMPIAR-10052-RING_1', en.full_name_upper)  # different
        self.assertEqual('empiar-10052-ring_1', en.full_name_lower)  # different
        self.assertEqual('empiar_10052-ring_1.mrc', en.file_name)
        self.assertEqual('mrc', en.ext)

    def test_emdb_5dig(self):
        en = ImageName('EMD-10052')
        self.assertEqual('emdb', en.archive)
        with self.assertWarns(PendingDeprecationWarning):
            entry_id = en.id_only
            self.assertEqual('10052', entry_id)
        self.assertEqual('emd_10052', en.canonical_name)
        self.assertEqual('EMD-10052', en.uppercase_hyphen_name)
        self.assertEqual('EMD_10052', en.uppercase_underscore_name)
        self.assertEqual('emd-10052', en.lowercase_hyphen_name)
        self.assertEqual('emd_10052', en.lowercase_underscore_name)
        self.assertEqual('EMD-10052', en.full_name_upper)
        self.assertEqual('emd-10052', en.full_name_lower)
        self.assertEqual('EMD-10052.map', en.file_name)
        self.assertEqual('map', en.ext)

    def test_emdb_4dig(self):
        en = ImageName('EMD-1832')
        self.assertEqual('emdb', en.archive)
        self.assertEqual('1832', en.id_only)
        self.assertEqual('emd_1832', en.canonical_name)
        self.assertEqual('EMD-1832', en.uppercase_hyphen_name)
        self.assertEqual('EMD_1832', en.uppercase_underscore_name)
        self.assertEqual('emd-1832', en.lowercase_hyphen_name)
        self.assertEqual('emd_1832', en.lowercase_underscore_name)
        self.assertEqual('EMD-1832', en.full_name_upper)
        self.assertEqual('emd-1832', en.full_name_lower)
        self.assertEqual('EMD-1832.map', en.file_name)
        self.assertEqual('map', en.ext)

    @staticmethod
    def get_image_ids(db_string, image_name, ext):
        """
        Get image IDs from OMERO DB
        """
        image_ids = {
            'top': None, 'front': None, 'side': None,
            'top-thumb': None, 'front-thumb': None, 'side-thumb': None,
        }

        with psycopg2.connect(db_string) as conn:
            try:
                cur = conn.cursor()
            except Exception as e:
                print(str(e))
                return image_ids
            else:
                # top image id
                try:
                    _image_name = '{}-top.{}'.format(image_name, ext)
                    print('top image: {}'.format(_image_name))
                    cur.execute("""SELECT id from image WHERE image.name = '{}'""".format(_image_name))
                    rows = cur.fetchall()
                    if len(rows) > 1:
                        print(
                            'Too many ({}) images for top image. Image must be unique. Picking first...'.format(
                                _image_name))
                    image_ids['top'] = rows[0][0]
                except Exception as e:
                    print(str(e))

                # front image id
                try:
                    _image_name = '{}-front.{}'.format(image_name, ext)
                    cur.execute("""SELECT id from image WHERE image.name = '{}'""".format(_image_name))
                    rows = cur.fetchall()
                    if 0 < len(rows) > 1:
                        print(
                            'Too many ({}) images for front image. Image must be unique. Picking first...'.format(
                                _image_name))
                    image_ids['front'] = rows[0][0]
                except Exception as e:
                    print(str(e))

                # side image id
                try:
                    _image_name = '{}-right.{}'.format(image_name, ext)
                    cur.execute("""SELECT id from image WHERE image.name = '{}'""".format(_image_name))
                    rows = cur.fetchall()
                    if 0 < len(rows) > 1:
                        print(
                            'Too many ({}) images for side image. Image must be unique. Picking first...'.format(
                                _image_name))
                    image_ids['side'] = rows[0][0]
                except Exception as e:
                    print(str(e))

                # top-thumb image id
                try:
                    _image_name = '{}-top-thumb.{}'.format(image_name, ext)
                    cur.execute("""SELECT id from image WHERE image.name = '{}'""".format(_image_name))
                    rows = cur.fetchall()
                    if len(rows) > 1:
                        print(
                            'Too many ({}) images for top-thumb image. Image must be unique. Picking first...'.format(
                                _image_name))
                    image_ids['top-thumb'] = rows[0][0]
                except Exception as e:
                    print(str(e))

                # front-thumb image id
                try:
                    _image_name = '{}-front-thumb.{}'.format(image_name, ext)
                    cur.execute("""SELECT id from image WHERE image.name = '{}'""".format(_image_name))
                    rows = cur.fetchall()
                    if 0 < len(rows) > 1:
                        print(
                            'Too many ({}) images for front-thumb image. Image must be unique. Picking first...'.format(
                                _image_name))
                    image_ids['front-thumb'] = rows[0][0]
                except Exception as e:
                    print(str(e))

                # side-thumb image id
                try:
                    _image_name = '{}-right-thumb.{}'.format(image_name, ext)
                    cur.execute("""SELECT id from image WHERE image.name = '{}'""".format(_image_name))
                    rows = cur.fetchall()
                    if 0 < len(rows) > 1:
                        print(
                            'Too many ({}) images for side-thumb image. Image must be unique. Picking first...'.format(
                                _image_name))
                    image_ids['side-thumb'] = rows[0][0]
                except Exception as e:
                    print(str(e))

        return image_ids

    @staticmethod
    def get_image_params(db_string, image_name, ext, top_id):
        """
        Get image params depending on entry type
        """
        image_params = {
            'x-size': None,
            'y-size': None,
            'z-size': None,
            'contrast_min': None,
            'contrast_max': None,
        }

        with psycopg2.connect(db_string) as conn:
            try:
                cur = conn.cursor()
            except Exception as e:
                print(str(e))
                return image_params
            else:
                _image_name = '{}-front.{}'.format(image_name, ext)
                try:
                    query = """SELECT sizex,sizey,sizez from pixels WHERE name = '{}'""".format(_image_name)
                    cur.execute(
                        query)  # + """' AND image.owner_id = 2""")
                    rows = cur.fetchall()
                    image_params['x-size'], image_params['y-size'], image_params['z-size'] = rows[0]
                except Exception:
                    print('Could not find image sizes')
                try:
                    contrast_min, contrast_max = get_fb_channel(top_id)
                    image_params['contrast_min'], image_params['contrast_max'] = contrast_min, contrast_max
                except Exception:
                    print('Could not find image contrast values; using defaults (min, max) = (0, 65535)')
                    image_params['contrast_min'] = 0
                    image_params['contrast_max'] = 65535

        return image_params

    @staticmethod
    def get_data_from_db(db_string, entry_name):
        data_from_db = list()
        # fixme: referring to a deprecated attribute
        if entry_name.matched:
            # regex rooted on entry name
            query = f"select * from empiar.image where empiar.image.name ~ '^{entry_name.lowercase_underscore_name}([-_].*)*-top\.(map|mrc)$'"
            # search the omero postgres db for the image name
            with psycopg2.connect(db_string) as conn:
                cur = conn.cursor()
                cur.execute(query)
                data_from_db = cur.fetchall()
        return data_from_db

    @staticmethod
    def parse_data(entry_name, data_from_db):
        CANONICAL_NAME_RE = r"^(?P<canonical_entry_name>(empiar|emp|EMP|EMPIAR|emd|emdb|EMD|EMDB)[-_]\d{4,5}.*?)\-top\.(map|mrc)$"
        DESCRIPTION_IN_CANONICAL_NAME_RE = r"(empiar|emp|EMP|EMPIAR|emd|emdb|EMD|EMDB)[-_]\d{4,5}[-_](?P<description>.*)$"
        data = {
            'volumes': list()
        }
        # if we have any data then we will compile a list of objects
        for row in data_from_db:
            # for each row of data
            canonical_name_match = re.match(
                CANONICAL_NAME_RE,
                row[5]
            )
            if canonical_name_match:
                canonical_name = canonical_name_match.group('canonical_entry_name')
                description_match = re.match(DESCRIPTION_IN_CANONICAL_NAME_RE, canonical_name)
                if description_match:
                    description = description_match.group('description').upper()
                else:
                    description = _EntryName(
                        canonical_name).uppercase_hyphen_name
                # determine the url depending on the archive
                if entry_name.archive == 'emdb':
                    url = f"/empiar/volume-browser/{canonical_name}"  # reverse_lazy('empiar3d:emdb-entry', kwargs={'entry_name': canonical_name})
                elif entry_name.archive == 'empiar':
                    url = f"/empiar/volume-browser/{canonical_name}"  # reverse_lazy('empiar3d:empiar-entry', kwargs={'entry_name': canonical_name})
                else:
                    url = None
                # only return something if we have a valid url
                if url is not None:
                    entry_data = {
                        'image_id': row[0],
                        'accession': ImageName(canonical_name).uppercase_hyphen_name,
                        'image_name': canonical_name,
                        'url': url,
                        'description': description,
                    }
                    data['volumes'].append(entry_data)
                else:
                    print(f"error: unknown archive '{entry_name.archive}'", file=sys.stderr)
            else:
                print(f"info: no match for entry {self.kwargs.get('entry_name')}", file=sys.stderr)
        return data

    def test_get_image_ids(self):
        """Test that we can correctly get image ids as in VB"""
        db_string = "dbname=empe3dstg user=empiar password=pmestgpwd host=pgsql-hxvm-044.ebi.ac.uk port=5432"
        # EMDB
        entry_name = ImageName('EMD-1832')
        image_ids = self.get_image_ids(db_string, entry_name.lowercase_underscore_name, entry_name.ext)
        self.assertIsInstance(image_ids['top'], int)
        self.assertIsInstance(image_ids['front'], int)
        self.assertIsInstance(image_ids['side'], int)
        self.assertIsInstance(image_ids['top-thumb'], int)
        self.assertIsInstance(image_ids['front-thumb'], int)
        self.assertIsInstance(image_ids['side-thumb'], int)
        # EMPIAR
        entry_name = ImageName('empiar_10461-survey_image_binned_4')
        image_ids = self.get_image_ids(db_string, entry_name.canonical_name, entry_name.ext)
        self.assertIsInstance(image_ids['top'], int)
        self.assertIsInstance(image_ids['front'], int)
        self.assertIsInstance(image_ids['side'], int)
        self.assertIsInstance(image_ids['top-thumb'], int)
        self.assertIsInstance(image_ids['front-thumb'], int)
        self.assertIsInstance(image_ids['side-thumb'], int)

    def test_emdb_api(self):
        """Test that we can get data from EMDB REST API"""
        # all/ endpoint
        emdb_rest_api = "https://www.ebi.ac.uk/pdbe/api/emdb/entry/"
        entry_name = ImageName('EMD-1832')
        r = requests.get(emdb_rest_api + "all/" + entry_name.uppercase_hyphen_name, verify=False)
        fast_axis = r.json()[entry_name.uppercase_hyphen_name][0]["map"]["axis_order"]["fast"]
        self.assertTrue(fast_axis in 'XYZ')
        # analysis/ endpoint
        s = requests.get(emdb_rest_api + "analysis/" + entry_name.full_name_upper, verify=False)
        histogram = s.json()[entry_name.uppercase_hyphen_name][0]["density_distribution"]
        print(histogram)
        self.assertIsInstance(histogram, dict)
        self.assertTrue(len(histogram) > 0)
        self.assertTrue("y" in histogram)
        self.assertTrue("x" in histogram)
        self.assertIsInstance(histogram["x"], list)
        self.assertIsInstance(histogram["y"], list)

    def test_empiar_api(self):
        """Test that we can correctly get data from the EMPIAR REST API"""
        empiar_rest_api = "https://www.ebi.ac.uk/empiar/api/entry/"
        entry_name = ImageName("empiar_10461-survey_image_binned_4")
        r = requests.get(empiar_rest_api + "all/" + entry_name.uppercase_hyphen_name)
        entry_info = r.json()[entry_name.uppercase_hyphen_name]
        self.assertIsInstance(entry_info, dict)
        self.assertTrue(len(entry_info) > 0)
        self.assertTrue('imagesets' in entry_info)
        self.assertIsInstance(entry_info['imagesets'], list)

    def test_get_image_params(self):
        """Test that the get_image_params for EMPIAR entries"""
        db_string = "dbname=empe3dstg user=empiar password=pmestgpwd host=pgsql-hxvm-044.ebi.ac.uk port=5432"
        entry_name = ImageName('empiar_10461-survey_image_binned_4')
        image_ids = self.get_image_ids(db_string, entry_name.canonical_name, entry_name.ext)
        image_params = self.get_image_params(db_string, entry_name.canonical_name, entry_name.ext, image_ids['top'])
        self.assertTrue('x-size' in image_params)
        self.assertTrue('y-size' in image_params)
        self.assertTrue('z-size' in image_params)
        self.assertTrue('contrast_min' in image_params)
        self.assertTrue('contrast_max' in image_params)
        self.assertIsInstance(image_params['x-size'], int)
        self.assertIsInstance(image_params['y-size'], int)
        self.assertIsInstance(image_params['z-size'], int)
        self.assertIsInstance(image_params['contrast_min'], int)
        self.assertIsInstance(image_params['contrast_max'], int)

    def test_get_data_from_db(self):
        """Test for EntryURL view"""
        db_string = "dbname=empe3dstg user=empiar password=pmestgpwd host=pgsql-hxvm-044.ebi.ac.uk port=5432"
        entry_name = ImageName('EMPIAR-10461')
        data_from_db = self.get_data_from_db(db_string, entry_name)
        self.assertIsInstance(data_from_db, list)
        # at least one result
        self.assertTrue(len(data_from_db) >= 1)
        data = self.parse_data(entry_name, data_from_db)
        self.assertIsInstance(data, dict)
        self.assertIn('volumes', data)
        self.assertIsInstance(data['volumes'], list)
        self.assertIn('image_id', data['volumes'][0])
        self.assertIn('accession', data['volumes'][0])
        self.assertIn('image_name', data['volumes'][0])
        self.assertIn('url', data['volumes'][0])
        self.assertIn('description', data['volumes'][0])
        self.assertEqual('EMPIAR-10461', data['volumes'][0]['accession'])  # at least the accession should be consistent


_annotation_attrs = [
    'canonical_name',
    'annotation_name',
    'uppercase_hyphen_name',
    'lowercase_hyphen_name',
    'uppercase_underscore_name',
    'lowercase_underscore_name',
    'full_name_upper',
    'full_name_lower',
    'file_name',
]


class TestAnnotationName(unittest.TestCase):
    def test_emdb_defaults(self):
        """Test that even if we fail to parse the given name we have some values"""
        an = AnnotationName('emd1234')
        self.assertFalse(an.is_test)
        self.assertIsNone(an.archive)
        self.assertIsNone(an.entry_id)
        self.assertIsNone(an.suffix)
        self.assertEqual('sff', an.ext)
        self.assertIsNone(an.qualifier)
        self.assertIsNone(an.noid)
        self.assertEqual('', an.entry_subtree)
        for attr in _annotation_attrs:
            self.assertIsNone(getattr(an, attr))
        # good file
        an = AnnotationName('emd_1234-oZRVsrr.hff', verbose=True)
        self.assertFalse(an.is_test)
        self.assertEqual('emdb', an.archive)
        self.assertEqual('1234', an.entry_id)
        self.assertEqual('-oZRVsrr', an.suffix)
        self.assertEqual('hff', an.ext)
        self.assertEqual('', an.qualifier)
        self.assertEqual('oZRVsrr', an.noid)
        self.assertEqual('12/1234/oZRVsrr/', an.entry_subtree)
        # required attributes
        values = [
            'emd_1234',
            'emd_1234-oZRVsrr',
            'EMD-1234',
            'emd-1234',
            'EMD_1234',
            'emd_1234',
            'EMD-1234-oZRVsrr',
            'emd-1234-oZRVsrr',
            'emd_1234-oZRVsrr.hff',
        ]
        for i, attr in enumerate(_annotation_attrs):
            expected_value = values[i]
            value = getattr(an, attr)
            self.assertEqual(expected_value, value)
        # test file
        an = AnnotationName('test-emd_1234-oZRVsrr.sff', verbose=True)
        self.assertTrue(an.is_test)

    def test_empiar_defaults(self):
        """Test that even if we fail to parse the given name we have some values"""
        an = AnnotationName('empiar1234-some.other-var-oZRVsrr.sff')
        self.assertFalse(an.is_test)
        self.assertIsNone(an.archive)
        self.assertIsNone(an.entry_id)
        self.assertIsNone(an.suffix)
        self.assertEqual('sff', an.ext)
        self.assertIsNone(an.qualifier)
        self.assertIsNone(an.noid)
        self.assertEqual('', an.entry_subtree)
        for attr in _annotation_attrs:
            self.assertIsNone(getattr(an, attr))
        # good file
        an = AnnotationName('empiar_12345-some.other_value-oZRVsrr.json', verbose=True)
        self.assertFalse(an.is_test)
        self.assertEqual('empiar', an.archive)
        self.assertEqual('12345', an.entry_id)
        self.assertEqual('-some.other_value-oZRVsrr', an.suffix)
        self.assertEqual('json', an.ext)
        self.assertEqual('-some.other_value', an.qualifier)
        self.assertEqual('oZRVsrr', an.noid)
        self.assertEqual('empiar_12345/empiar_12345-some.other_value/oZRVsrr/', an.entry_subtree)
        # required attributes
        values = [
            'empiar_12345-some.other_value',
            'empiar_12345-some.other_value-oZRVsrr',
            'EMPIAR-12345',
            'empiar-12345',
            'EMPIAR_12345',
            'empiar_12345',
            'EMPIAR-12345-SOME.OTHER_VALUE-oZRVsrr',
            'empiar-12345-some.other_value-oZRVsrr',
            'empiar_12345-some.other_value-oZRVsrr.json',
        ]
        for i, attr in enumerate(_annotation_attrs):
            expected_value = values[i]
            value = getattr(an, attr)
            self.assertEqual(expected_value, value)
        # test file
        an = AnnotationName('test-empiar_12345-some.other_value-oZRVsrr.sff', verbose=True)
        self.assertTrue(an.is_test)

    def test_empiar(self):
        # with extension
        an = AnnotationName('empiar_10052-ring_1-oZRVsrr.hff', verbose=True)
        self.assertEqual('empiar', an.archive)
        self.assertEqual('10052', an.entry_id)
        self.assertEqual('empiar_10052-ring_1', an.canonical_name)
        self.assertEqual('empiar_10052-ring_1-oZRVsrr', an.annotation_name)
        self.assertEqual('EMPIAR-10052', an.uppercase_hyphen_name)
        self.assertEqual('EMPIAR_10052', an.uppercase_underscore_name)
        self.assertEqual('empiar-10052', an.lowercase_hyphen_name)
        self.assertEqual('empiar_10052', an.lowercase_underscore_name)
        self.assertEqual('EMPIAR-10052-RING_1-oZRVsrr', an.full_name_upper)
        self.assertEqual('empiar-10052-ring_1-oZRVsrr', an.full_name_lower)
        self.assertEqual('empiar_10052-ring_1-oZRVsrr.hff', an.file_name)
        self.assertEqual('-ring_1-oZRVsrr', an.suffix)
        self.assertEqual('-ring_1', an.qualifier)
        self.assertEqual('hff', an.ext)
        self.assertEqual('oZRVsrr', an.noid)
        self.assertFalse(an.is_valid())
        self.assertEqual('empiar_10052/empiar_10052-ring_1/oZRVsrr/', an.entry_subtree)
        # without extension
        an = AnnotationName('empiar_10052-ring_1-oZRVsrr', verbose=True)
        self.assertEqual('empiar', an.archive)
        self.assertEqual('10052', an.entry_id)
        self.assertEqual('empiar_10052-ring_1', an.canonical_name)
        self.assertEqual('EMPIAR-10052', an.uppercase_hyphen_name)
        self.assertEqual('EMPIAR_10052', an.uppercase_underscore_name)
        self.assertEqual('empiar-10052', an.lowercase_hyphen_name)
        self.assertEqual('empiar_10052', an.lowercase_underscore_name)
        self.assertEqual('EMPIAR-10052-RING_1-oZRVsrr', an.full_name_upper)
        self.assertEqual('empiar-10052-ring_1-oZRVsrr', an.full_name_lower)
        self.assertEqual('empiar_10052-ring_1-oZRVsrr.sff', an.file_name)
        self.assertEqual('-ring_1-oZRVsrr', an.suffix)
        self.assertEqual('-ring_1', an.qualifier)
        self.assertEqual('sff', an.ext)
        self.assertEqual('oZRVsrr', an.noid)
        self.assertFalse(an.is_valid())
        self.assertEqual('empiar_10052/empiar_10052-ring_1/oZRVsrr/', an.entry_subtree)

    def test_emdb_5dig(self):
        # with extension
        an = AnnotationName('EMD-10052-YPELSCM.json')
        self.assertEqual('emdb', an.archive)
        self.assertEqual('10052', an.entry_id)
        self.assertEqual('emd_10052', an.canonical_name)
        self.assertEqual('emd_10052-YPELSCM', an.annotation_name)
        self.assertEqual('EMD-10052', an.uppercase_hyphen_name)
        self.assertEqual('EMD_10052', an.uppercase_underscore_name)
        self.assertEqual('emd-10052', an.lowercase_hyphen_name)
        self.assertEqual('emd_10052', an.lowercase_underscore_name)
        self.assertEqual('EMD-10052-YPELSCM', an.full_name_upper)
        self.assertEqual('emd-10052-YPELSCM', an.full_name_lower)
        self.assertEqual('EMD-10052-YPELSCM.json', an.file_name)
        self.assertEqual('-YPELSCM', an.suffix)
        self.assertEqual('', an.qualifier)
        self.assertEqual('json', an.ext)
        self.assertEqual('YPELSCM', an.noid)
        self.assertTrue(an.is_valid())
        self.assertEqual('10/0/10052/YPELSCM/', an.entry_subtree)
        # without extension
        an = AnnotationName('EMD-10052-YPELSCM')
        self.assertEqual('emdb', an.archive)
        self.assertEqual('10052', an.entry_id)
        self.assertEqual('emd_10052', an.canonical_name)
        self.assertEqual('EMD-10052', an.uppercase_hyphen_name)
        self.assertEqual('EMD_10052', an.uppercase_underscore_name)
        self.assertEqual('emd-10052', an.lowercase_hyphen_name)
        self.assertEqual('emd_10052', an.lowercase_underscore_name)
        self.assertEqual('EMD-10052-YPELSCM', an.full_name_upper)
        self.assertEqual('emd-10052-YPELSCM', an.full_name_lower)
        self.assertEqual('EMD-10052-YPELSCM.sff', an.file_name)
        self.assertEqual('-YPELSCM', an.suffix)
        self.assertEqual('', an.qualifier)
        self.assertEqual('sff', an.ext)
        self.assertEqual('YPELSCM', an.noid)
        self.assertTrue(an.is_valid())
        self.assertEqual('10/0/10052/YPELSCM/', an.entry_subtree)

    def test_emdb_4dig(self):
        an = AnnotationName('EMD-1832-ZR56MM2')
        self.assertEqual('emdb', an.archive)
        self.assertEqual('1832', an.entry_id)
        self.assertEqual('emd_1832', an.canonical_name)
        self.assertEqual('emd_1832-ZR56MM2', an.annotation_name)
        self.assertEqual('EMD-1832', an.uppercase_hyphen_name)
        self.assertEqual('EMD_1832', an.uppercase_underscore_name)
        self.assertEqual('emd-1832', an.lowercase_hyphen_name)
        self.assertEqual('emd_1832', an.lowercase_underscore_name)
        self.assertEqual('EMD-1832-ZR56MM2', an.full_name_upper)
        self.assertEqual('emd-1832-ZR56MM2', an.full_name_lower)
        self.assertEqual('EMD-1832-ZR56MM2.sff', an.file_name)
        self.assertEqual('-ZR56MM2', an.suffix)
        self.assertEqual('', an.qualifier)
        self.assertEqual('sff', an.ext)
        self.assertEqual('ZR56MM2', an.noid)
        self.assertTrue(an.is_valid())
        self.assertEqual('18/1832/ZR56MM2/', an.entry_subtree)

    def test_emdb_qualifier(self):
        an = AnnotationName('emd_8750_v0.8.0.dev1-ehyZGZS')
        self.assertEqual('emdb', an.archive)
        self.assertEqual('8750', an.entry_id)
        self.assertEqual('emd_8750', an.canonical_name)
        self.assertEqual('emd_8750-ehyZGZS', an.annotation_name)
        self.assertEqual('EMD-8750', an.uppercase_hyphen_name)
        self.assertEqual('EMD_8750', an.uppercase_underscore_name)
        self.assertEqual('emd-8750', an.lowercase_hyphen_name)
        self.assertEqual('emd_8750', an.lowercase_underscore_name)
        self.assertEqual('EMD-8750_V0.8.0.DEV1-ehyZGZS', an.full_name_upper)
        self.assertEqual('emd-8750_v0.8.0.dev1-ehyZGZS', an.full_name_lower)
        self.assertEqual('emd_8750_v0.8.0.dev1-ehyZGZS.sff', an.file_name)
        self.assertEqual('_v0.8.0.dev1-ehyZGZS', an.suffix)
        self.assertEqual('_v0.8.0.dev1', an.qualifier)
        self.assertEqual('sff', an.ext)
        self.assertEqual('ehyZGZS', an.noid)
        self.assertTrue(an.is_valid())
        self.assertEqual('87/8750/ehyZGZS/', an.entry_subtree)

    def test_exotic_entry_names(self):
        image_names = [
            "empiar_10324_em04226_2_u19_cropped_yz_binned",
            "empiar_10052-ring_1",
            "empiar_10053-trophozoite_1",
            "empiar_10070_b3talongmusc20130301",
            "empiar_10087_c2_tomo02",
            "empiar_10087_e64_tomo03",
            "empiar_10147-g66-68",
            "empiar_10147-g55-57",
            "empiar_10147-g58-60",
            "empiar_10327-p0466_em04220_d19_cropped_yz_binned",
            "empiar_10442-170821_col-0_r01_294-317um",
            "empiar_10442-180130_plm_se_up_278-307um",
            "empiar_10442-170314_col-0_r20_339-381um",
            "empiar_10442-180130_plm_se_down_278-307um",
            "empiar_10331-ds2-binned-8",
            "empiar_10331-tf21-binned-8",
            "empiar_10092-3vbsed-roi",
            "empiar_10054-e-schizont_1",
            "empiar_10055-l-schizont_2",
            "empiar_10624-20200311_tomo03_3ds30_man",
            "empiar_10624-20200311_tomo04_3ds30_man",
            "empiar_10624-20200312_tomo23_3ds30_man",
            "empiar_10094-hela_binned_4",
            "empiar_10100-anaphase_3.1min_binned_2",
            "empiar_10102-anaphase_3.9min_binned_4",
            "empiar_10103-anaphase_4.3min_binned_4",
            "empiar_10101-anaphase_6.3min_binned_4",
            "empiar_10104-anaphase_5.3min_binned_4",
            "empiar_10105-anaphase_5.1min_binned_4",
            "empiar_10148-postnatal_guinea_pig_heart_neonate",
            "empiar_10148-postnatal_guinea_pig_heart_adult",
            "empiar_10149-prenatal_guinea_pig_left_ventricle_g55-57",
            "empiar_10149-prenatal_guinea_pig_left_ventricle_g58-60",
            "empiar_10149-prenatal_guinea_pig_left_ventricle_g66-68",
            "empiar_10150-prenatal_guinea_pig_heart_adult",
            "empiar_10150-prenatal_guinea_pig_heart_neonate",
            "empiar_10151-prenatal_guinea_pig_lv_g58-60_binned_2",
            "empiar_10151-prenatal_guinea_pig_lv_g55-57",
            "empiar_10151-prenatal_guinea_pig_lv_g66-68",
            "empiar_10312-animal1_ct1_sample2_headdown_binned_2",
            "empiar_10152-optic_lobe_adult_locust_binned_4",
            "empiar_10312-animal2_ct2_sample8_headup_binned_2",
            "empiar_10312-animal1_ct2_sample4_headdown_binned_2",
            "empiar_10312-animal3_ct1_sample11_headright_binned_4",
            "empiar_10312-animal1_la1_sample1_headright_binned_2",
            "empiar_10312-animal2_ct1_sample7_headup_binned_2",
            "empiar_10312-animal3_la2_sample10_headright_binned_4",
            "empiar_10312-animal3_la1_sample9_headright_binned_4",
            "empiar_10312-animal3_ct2_sample12_headright_binned_4",
            "empiar_10312-animal1_la2_sample5_headup_binned_2",
            "empiar_10312-animal2_la1_sample3_headup_binned_2",
            "empiar_10312-animal2_la2_sample6_headup_binned_2",
            "empiar_10311-20140801_hela-wt_xy5z8nm_as-template_match_aligned_binned_4",
            "empiar_10310-20180813_platynereis_parapodia-sift_aligned_binned_2",
            "empiar_10310-20180813_platynereis_parapodia-amst_aligned_binned_2",
            "empiar_10311-20140801_hela-wt_xy5z8nm_as-raw_8bit_binned_4",
            "empiar_10311-20140801_hela-wt_xy5z8nm_as-amst_aligned_binned_4",
            "empiar_10310-20180813_platynereis_parapodia-raw_16bit_binned_2",
            "empiar_10434-c01",
            "empiar_10434-dynamin_inactivation_1hr",
            "empiar_10434-c02",
            "empiar_10434-dynamic_inactivation_2hrs",
            "empiar_10478-roi_4320-1260-95",
            "empiar_10478-roi_1716-7800-517",
            "empiar_10478-roi_3624-2712-201",
            "empiar_10478-roi_3588-3972-1",
            "empiar_10478-roi_2820-6780-468",
            "empiar_10478-roi_2448-4704-271",
            "empiar_10478-roi_3768-7248-143",
            "empiar_10478-roi_1584-6996-1",
            "empiar_10478-roi_3000-3264-393",
            "empiar_10478-roi_3972-1956-438",
            "empiar_10478-roi_3516-5712-314",
            "empiar_10478-roi_1656-6756-329",
            "empiar_10478-roi_1608-912-1",
            "empiar_10478-roi_1536-3456-213",
            "empiar_10478-roi_3576-5232-35",
            "empiar_10478-roi_2052-5784-112",
            "empiar_10478-roi_2832-1692-1",
            "empiar_10478-roi_1416-1932-171",
            "empiar_10672-symbiotic-cell_40plastids",
            "empiar_10672-symbiotic-cell_16plastids",
            "empiar_10672-symbiotic-cell_36plastids",
            "empiar_10672-freeling-phaeocystis-14cells",
            "empiar_10672-symbiotic-cell_65plastids",
            "empiar_10672-symbiotic-cell_54plastids",
            "empiar_10672-symbiotic-cell_31plastids",
            "empiar_10672-symbiotic-cell_4plastids",
            "empiar_10490-fib-sem_s4_cell1_5nm_3dbinned_8",
            "empiar_10479-fib_sem",
            "empiar_10414-u2os_reo_1hpi_area1_reconstruction",
            "empiar_10415-u2os_reo_1hpi_area2_reconstruction",
            "empiar_10417-u2os_reo_2hpi_area2_reconstruction",
            "empiar_10419-u2os_reo_4hpi_area2_reconstruction",
            "empiar_10412-u2os_reo_mockinfected_area1_reconstruction",
            "empiar_10416-u2os_reo_2hpi_area1_reconstruction",
            "empiar_10418-u2os_reo_4hpi_area1_reconstruction",
            "empiar_10413-u2os_reo_mockinfected_area2_reconstruction",
            "empiar_10460-6800x_t3_all_binned_2",
            "empiar_10460-6800x_t1_all_binned_2",
            "empiar_10460-6800x_t2_all_binned_2",
            "empiar_10515-raw_patient_release_binned_2",
            "empiar_10515-raw_control_release_binned_2",
            "empiar_10459-raw_part_2_binned_8",
            "empiar_10459-raw_part_1_binned_8",
            "empiar_10459-fib_fish3_section1_xz_macrophage_5nm3_binned_2",
            "empiar_10490-fib-sem_s5_mock_cell1_2_3dbinned_4",
            "empiar_10490-fib-sem_s4_area3_3dbinned_4",
            "empiar_10490-fib-sem_s4_area2_3dbinned_4",
            "empiar_10553-seeger_5_reg",
            "empiar_10554-aligned_464_of_464",
            "empiar_10618-03_tomo_t9_g1_f3f_area2",
            "empiar_10617-11_tomo_e4c1_wbp",
            "empiar_10618-02_tomo_t9_g1_f3f",
            "empiar_10618-03_tomo_t9_g1_f3f_area2_full",
            "empiar_10619-09_tomo_t10g2_d2c_full",
            "empiar_10622-02_tomo_f4a",
            "empiar_10622-02_tomo_f4a_full",
            "empiar_10620-06_tomo_g4c_area2",
            "empiar_10563-raw_tomogram_data_binned_2",
            "empiar_10562-raw_tomogram_data_binned_2",
            "empiar_10620-05_tomo_g4c_area1",
            "empiar_10620-06_tomo_g4c_area2_full",
            "empiar_10620-05_tomo_g4c_area1_full",
            "empiar_10619-09_tomo_t10g2_d2c",
        ]
        for image_name in image_names:
            annot_name = f"{image_name}-{noid.mint(template='zeeeeeek')}.sff"
            an = AnnotationName(annot_name)
            self.assertTrue(an.is_valid())

    def test_fail(self):
        an = AnnotationName('emd1234', verbose=True)
        self.assertIsNone(an.canonical_name)
