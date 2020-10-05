import unittest

import sep.loaders.images
import sep.process
import sep.producers.producer
import sep.savers.images
import tests.testbase


class TestProcess(tests.testbase.TestBase):
    class Threshold(sep.producers.ImagesProducer):
        def __init__(self, name, channel, cache_root):
            super().__init__(name=name, cache_root=cache_root)
            self.channel = channel

        def segmentation(self, image, image_tag):
            return image[..., self.channel] > 200

    def test_process_simple(self):
        output_dir = self.create_temp_dir()
        test_images_loader = sep.loaders.images.ImagesLoader(self.root_test_dir("input/lights"))
        test_images_savers = sep.savers.images.ImagesSaver()
        producer_red = self.Threshold("Red", 0, self.create_temp_dir())

        sep.process.process(test_images_loader, producer_red, test_images_savers, output_dir)
        output_loader = sep.loaders.images.ImagesLoader(output_dir)
        self.assertEqual(len(test_images_loader), len(output_loader))


if __name__ == '__main__':
    unittest.main()
