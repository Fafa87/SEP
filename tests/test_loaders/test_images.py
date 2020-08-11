import unittest

from sep.loaders.images import ImagesLoader
import numpy.testing as nptest


class TestImagesLoader(unittest.TestCase):
    def test_loading(self):
        test_images_loader = ImagesLoader("input")
        self.assertEqual(2, len(test_images_loader))
        self.assertEqual(['lights01', 'lights02'], test_images_loader.input_order)

        input_data_02_by_id = test_images_loader.load_image(1)
        input_data_02_by_name = test_images_loader.load_image('lights02')
        nptest.assert_equal(input_data_02_by_id, input_data_02_by_name)

        self.assertIsNone(test_images_loader.load_tag('lights02'))
        self.assertIsNone(test_images_loader.load_tag('lights10'))

        annotation_1 = test_images_loader.load_annotation(0)
        self.assertEqual(annotation_1.shape, input_data_02_by_id.shape[:2])
        self.assertEqual(255, annotation_1.max())


if __name__ == '__main__':
    unittest.main()
