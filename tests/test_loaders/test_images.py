import numpy.testing as nptest
import os
import unittest

from sep.loaders.images import ImagesLoader
from tests.testbase import TestBase


class TestImagesLoader(TestBase):
    def test_loading(self):
        test_images_loader = ImagesLoader(self.root_test_dir("input/lights"))
        self.assertEqual(2, len(test_images_loader))
        self.assertEqual(['lights01', 'lights02'], test_images_loader.input_order)

        input_data_02_by_id = test_images_loader.load_image(1)
        input_data_02_by_name = test_images_loader.load_image('lights02')
        nptest.assert_equal(input_data_02_by_id, input_data_02_by_name)

        tag_02 = test_images_loader.load_tag('lights02')
        self.assertEqual("lights02", tag_02["id"])
        self.assertEqual("thenet", tag_02["source"])
        non_existing_tag10 = test_images_loader.load_tag('lights10')
        self.assertEqual("lights10", non_existing_tag10["id"])
        self.assertNotIn("source", non_existing_tag10)

        annotation_1 = test_images_loader.load_annotation(0)
        self.assertEqual(annotation_1.shape, input_data_02_by_id.shape[:2])
        self.assertEqual(255, annotation_1.max())

        tag_1 = test_images_loader.load_tag(0)
        self.assertEqual(0, tag_1["id"])  # TODO RETHINK default tags mirror exact call

    def test_get_element(self):
        test_images_loader = ImagesLoader(self.root_test_dir("input/lights"))
        second_elem = test_images_loader[1]
        self.assertIn("image", second_elem)
        self.assertIn("annotation", second_elem)
        self.assertIn("tag", second_elem)

    def test_iterate_through(self):
        test_images_loader = ImagesLoader(self.root_test_dir("input/lights"))
        data = [p for p in test_images_loader]
        self.assertEqual(2, len(data))
        second_elem = data[1]
        self.assertIn("image", second_elem)
        self.assertIn("annotation", second_elem)
        self.assertIn("tag", second_elem)

    def test_relative(self):
        test_images_loader = ImagesLoader(self.root_test_dir("input"))
        data_names = test_images_loader.list_images()
        self.assertEqual(5, len(data_names))
        self.assertEqual("human_1", data_names[0])
        self.assertEqual(os.path.join("humans", "human_1.tif"), test_images_loader.get_relative_path(0))
        self.assertEqual(os.path.join("humans", "human_1.tif"), test_images_loader.get_relative_path("human_1"))


if __name__ == '__main__':
    unittest.main()
