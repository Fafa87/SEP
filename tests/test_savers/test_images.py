import os
import unittest

import numpy as np
import numpy.testing as nptest

from sep._commons.utils import *
from sep.loaders import ImagesLoader
from sep.savers.images import ImagesSaver
from tests.testbase import TestBase


class TestImagesSaver(TestBase):
    def test_saving_in_hierarchy(self):
        test_images_loader = ImagesLoader.from_tree(self.root_test_dir("input/basics"))
        temp_dir = self.create_temp_dir()

        saver = ImagesSaver(temp_dir, test_images_loader)
        names = test_images_loader.list_images()
        self.assertEqual(7, len(names))
        self.assertEqual("human_1", names[0])
        known_name = "lights01"

        sample_res_1 = self.random_rgb((20, 20))
        sample_tag_1 = {"id": "human_1", "detail": 20}
        saver.save_result(0, sample_res_1)
        saver.save_tag(0, sample_tag_1, result_tag={"seg_confident": "no"})
        self.assertTrue(os.path.isfile(os.path.join(temp_dir, 'humans', 'human_1.png')))
        self.assertTrue(os.path.isfile(os.path.join(temp_dir, 'humans', 'human_1.json')))

        sample_res_2 = self.random_rgb((20, 20))
        saver.save_result(known_name, sample_res_2)
        self.assertTrue(os.path.isfile(os.path.join(temp_dir, 'lights', 'lights01.png')))

        saved_images_loader = ImagesLoader.from_tree(temp_dir)
        names = saved_images_loader.list_images()
        self.assertEqual(2, len(names))

        humans_saved = saved_images_loader['human_1']
        nptest.assert_almost_equal(humans_saved['image'], sample_res_1)
        self.assertEqual(humans_saved['tag'], union(sample_tag_1, {"seg_confident": "no"}))

        lights_saved = saved_images_loader['lights01']
        nptest.assert_almost_equal(lights_saved['image'], sample_res_2)
        self.assertEqual(lights_saved['tag'], {'id': 'lights01'})  # defaults


if __name__ == '__main__':
    unittest.main()
