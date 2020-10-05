import unittest

import numpy as np
import numpy.testing as nptest

import sep.producers
import tests.testbase


class TestProducer(tests.testbase.TestBase):
    class Threshold(sep.producers.ImagesProducer):
        def segmentation(self, image, image_tag):
            return image > 128

    def test_producer_calculate(self):
        random_soup = np.random.random((10, 10)) / 2.0
        random_soup[3:5, 6:9] = 1

        random_soup_tags = {"source": "dummies", "id": "soup"}

        thresh_producer = TestProducer.Threshold("DummyThreshold", cache_root=self.create_temp_dir())
        segm, producer_tags = thresh_producer.calculate(random_soup, random_soup_tags)

        self.assertEqual(2 * 3, segm.sum())
        self.assertIn("run_time", producer_tags)
        self.assertIn("run_fps", producer_tags)
        self.assertIn("producer_details", producer_tags)
        self.assertIn("DummyThreshold", producer_tags["producer_details"])
        # self.assertIn('producer-hash', producer_tags)

    def test_producer_cache(self):
        random_soup = np.random.random((10, 10)) / 2.0
        random_soup_tags = {"source": "dummies", "id": "soup"}

        thresh_producer = TestProducer.Threshold("DummyThreshold", cache_root=self.create_temp_dir())
        segm, producer_tags = thresh_producer.calculate(random_soup, random_soup_tags)

        nptest.assert_equal(segm, thresh_producer.load_segment(random_soup_tags["id"]))
        self.assertEqual(producer_tags, thresh_producer.load_tag(random_soup_tags["id"]))


if __name__ == '__main__':
    unittest.main()
