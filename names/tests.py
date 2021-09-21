import unittest

import noid

from . import ImageName, AnnotationName


class TestImageName(unittest.TestCase):
    def test_defaults(self):
        en = ImageName('emd1234')


    def test_empiar(self):
        en = ImageName('empiar_10052-ring_1')
        self.assertEqual('empiar', en.archive)
        self.assertEqual('10052', en.id_only)
        self.assertEqual('empiar_10052-ring_1', en.canonical_name)
        self.assertEqual('EMPIAR-10052', en.uppercase_hyphen_name)
        self.assertEqual('EMPIAR_10052', en.uppercase_underscore_name)
        self.assertEqual('empiar-10052', en.lowercase_hyphen_name)
        self.assertEqual('empiar_10052', en.lowercase_underscore_name)
        self.assertEqual('EMPIAR_10052-RING_1', en.full_name_upper)
        self.assertEqual('empiar_10052-ring_1', en.full_name_lower)
        self.assertEqual('empiar_10052-ring_1.mrc', en.file_name)
        self.assertEqual('mrc', en.ext)

    def test_emdb_5dig(self):
        en = ImageName('EMD-10052')
        self.assertEqual('emdb', en.archive)
        self.assertEqual('10052', en.id_only)
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
    def test_defaults(self):
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
        # test file
        an = AnnotationName('test-emd_1234-oZRVsrr.sff', verbose=True)
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
        self.assertEqual('EMPIAR-10052-oZRVsrr', an.full_name_upper)
        self.assertEqual('empiar-10052-oZRVsrr', an.full_name_lower)
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
        self.assertEqual('EMPIAR-10052-oZRVsrr', an.full_name_upper)
        self.assertEqual('empiar-10052-oZRVsrr', an.full_name_lower)
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
        self.assertEqual('EMD-8750-ehyZGZS', an.full_name_upper)
        self.assertEqual('emd-8750-ehyZGZS', an.full_name_lower)
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
