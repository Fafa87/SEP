import pathlib
import unittest

from tests.testbase import TestBase
from sep.loaders.images import ImagesLoader
import numpy.testing as nptest


class TestImagesLoader(TestBase):
    def test_loading(self):
        test_images_loader = ImagesLoader(TestBase.test_dir("input"))
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


if __name__ == '__main__':
    unittest.main()
