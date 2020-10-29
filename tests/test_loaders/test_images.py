from pathlib import Path

import numpy.testing as nptest
import os
import unittest

from sep.loaders.images import ImagesLoader
from tests.testbase import TestBase


class TestImagesLoader(TestBase):
    def test_loading(self):
        loader = ImagesLoader(self.root_test_dir("input/lights"))
        self.assertEqual(2, len(loader))
        self.assertEqual(['lights01', 'lights02'], loader.input_order)

        input_data_02_by_id = loader.load_image(1)
        input_data_02_by_name = loader.load_image('lights02')
        nptest.assert_equal(input_data_02_by_id, input_data_02_by_name)

        tag_02 = loader.load_tag('lights02')
        self.assertEqual("lights02", tag_02["id"])
        self.assertEqual("thenet", tag_02["source"])
        non_existing_tag10 = loader.load_tag('lights10')
        self.assertEqual("lights10", non_existing_tag10["id"])
        self.assertNotIn("source", non_existing_tag10)

        annotation_1 = loader.load_annotation(0)
        self.assertEqual(annotation_1.shape, input_data_02_by_id.shape[:2])
        self.assertEqual(255, annotation_1.max())

        tag_1 = loader.load_tag(0)
        self.assertEqual(0, tag_1["id"])  # TODO RETHINK default tags mirror exact call

    def test_get_element(self):
        loader = ImagesLoader(self.root_test_dir("input/lights"))
        second_elem = loader[1]
        self.assertIn("image", second_elem)
        self.assertIn("annotation", second_elem)
        self.assertIn("tag", second_elem)

    def test_iterate_through(self):
        loader = ImagesLoader(self.root_test_dir("input/lights"))
        data = [p for p in loader]
        self.assertEqual(2, len(data))
        second_elem = data[1]
        self.assertIn("image", second_elem)
        self.assertIn("annotation", second_elem)
        self.assertIn("tag", second_elem)

    def test_relative(self):
        loader = ImagesLoader(self.root_test_dir("input"))
        data_names = loader.list_images()
        self.assertEqual(5, len(data_names))
        self.assertEqual("human_1", data_names[0])
        self.assertEqual(os.path.join("humans", "human_1.tif"), loader.get_relative_path(0))
        self.assertEqual(os.path.join("humans", "human_1.tif"), loader.get_relative_path("human_1"))

    def test_listing_save(self):
        loader = ImagesLoader(self.root_test_dir("input"))
        data_names = loader.list_images()
        self.assertEqual(5, len(data_names))

        listing_path = self.add_temp("loader_listing.txt")
        loader.save(listing_path, add_tag_path=False)

        # check that there are 5 lines and that they point to the actual files
        with open(listing_path, "r") as listing_file:
            listing_lines = listing_file.readlines()
        self.assertEqual(5, len(listing_lines))
        self.assertEqual(f"{Path('humans/human_1.tif')}, {Path('humans/human_1_gt.png')}",
                         listing_lines[0].strip())

        loader.save(listing_path, add_tag_path=True)
        # now it has tag files (at least expected)
        with open(listing_path, "r") as listing_file:
            listing_lines = listing_file.readlines()
        self.assertEqual(f"{Path('humans/human_1.tif')}, {Path('humans/human_1_gt.png')}, {Path('humans/human_1.json')}",
                         listing_lines[0].strip())

    def test_listing_filter_load(self):
        loader = ImagesLoader(self.root_test_dir("input"))
        self.assertEqual(5, len(loader.list_images()))
        names = loader.list_images()
        #loader.filter_files([0, 2, 4])
        self.assertEqual(3, loader.list_images())
        self.assertEqual(names[::2], loader.list_images())

        listing_file = self.add_temp("loader_listing.txt")
        loader.save(listing_file, add_tag_path=False)

        # check that there are 3 lines and that they point to the actual files
        loader_reloaded = ImagesLoader.from_listing(self.root_test_dir("input"), file=listing_file)
        self.assertEqual(3, loader_reloaded.list_images())
        self.assertEqual(loader.list_images(), loader_reloaded.list_images())


if __name__ == '__main__':
    unittest.main()
