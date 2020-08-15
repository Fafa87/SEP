import unittest

import numpy as np
import numpy.testing as nptest

import sep.assessors.metricer
import sep.assessors.metrics
import sep.evaluate
import sep.loaders.images
import sep.producers.producer
import tests.testbase


class TestEvaluate(tests.testbase.TestBase):
    class Threshold(sep.producers.producer.Producer):
        def __init__(self, name, channel, cache_root):
            super().__init__(name=name, cache_root=cache_root)
            self.channel = channel

        def segmentation(self, image):
            return image[..., self.channel] > 200

    def test_evaluate_simple(self):
        test_images_loader = sep.loaders.images.ImagesLoader(self.test_dir("input/lights"))
        output_dir = self.create_temp_dir()

        producer_red = self.Threshold("Red", 0, self.create_temp_dir())
        metricer = sep.assessors.metricer.Metricer()
        metricer.metrics.append(sep.assessors.metrics.IouMetric())

        report_all = sep.evaluate.evaluate(data_loader=test_images_loader, producer=producer_red,
                                       metricer=metricer, detailer=None, output_evalpath=output_dir)
        report = metricer.report_full()

        self.assertEqual(2, len(report))
        nptest.assert_equal(report["id"].values, np.array([0, "lights02"], dtype=np.object))
        nptest.assert_equal(report["img_source"].values, ["", "thenet"])
        nptest.assert_equal(report["region"].values, ["Entire image", "Entire image"])
        self.assertIn("seg_run_time", report.columns)
        self.assertIn("seg_run_fps", report.columns)
        nptest.assert_equal(report["seg_producer_name"].values, ["Red", "Red"])
        self.assertTrue(report["iou"].values[0] > 0.3)

        self.assertEqual(1, len(report_all))
        indexes = list(report_all.index.values)
        nptest.assert_equal(indexes, [["Red", "Entire image"]])
        self.assertIn("seg_run_time", report.columns)
        self.assertIn("seg_run_fps", report.columns)
        self.assertTrue(report["iou"].values[0] > 0.3)





if __name__ == '__main__':
    unittest.main()
