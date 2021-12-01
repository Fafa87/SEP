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
    class Threshold(sep.producers.ImagesProducer):
        def __init__(self, name, channel, cache_root):
            super().__init__(name=name, cache_root=cache_root)
            self.channel = channel

        def segmentation(self, image, image_tag):
            return image[..., self.channel] > 200

    def test_evaluate_simple(self):
        test_images_loader = sep.loaders.images.ImagesLoader.from_tree(self.root_test_dir("input/basics/lights"))
        output_dir = self.create_temp_dir()

        producer_red = self.Threshold("Red", 0, self.create_temp_dir())
        metricer = sep.assessors.metricer.Metricer()
        metricer.metrics.append(sep.assessors.metrics.IouMetric())

        report_overall = sep.evaluate.evaluate(data_loader=test_images_loader, producer=producer_red,
                                               metricer=metricer, detailer=None, output_evalpath=output_dir)
        report = metricer.report_full()

        self.assertEqual(4, len(report))
        nptest.assert_equal(report["id"].values, np.array([0, "lights02", 2, 3], dtype=object))
        nptest.assert_equal(report["img_source"].values, ["", "thenet", "", ""])
        nptest.assert_equal(report["region"].values, ["Entire image", "Entire image", "Entire image", "Entire image"])
        self.assertIn("seg_run_time", report.columns)
        self.assertIn("seg_run_fps", report.columns)
        self.assertTrue(report["iou"].values[0] > 0.3)

        self.assertEqual(1, len(report_overall))
        indexes = list(report_overall.index.values)
        nptest.assert_equal(indexes, ["Entire image"])
        self.assertIn("seg_run_time", report_overall.columns)
        self.assertIn("seg_run_fps", report_overall.columns)
        self.assertTrue(report_overall["iou"].values[0] > 0.3)

    def test_compare_simple(self):
        test_images_loader = sep.loaders.images.ImagesLoader.from_tree(self.root_test_dir("input/basics/lights"))
        output_dir = self.create_temp_dir()

        producer_red = self.Threshold("Red", 0, self.create_temp_dir())
        producer_blue = self.Threshold("Green", 1, self.create_temp_dir())
        metricer = sep.assessors.metricer.Metricer()
        metricer.metrics.append(sep.assessors.metrics.IouMetric())

        report_overall = sep.evaluate.compare(data_loader=test_images_loader,
                                              producers=[producer_red, producer_blue],
                                              metricer=metricer, detailer=None,
                                              output_evalpath=output_dir)

        self.assertEqual(2, len(report_overall))
        indexes = list(report_overall.index.values)
        nptest.assert_equal(indexes, [["Green", "Entire image"],
                                      ["Red", "Entire image"]])
        self.assertIn("seg_run_time", report_overall.columns)
        self.assertIn("seg_run_fps", report_overall.columns)
        self.assertLess(report_overall["iou"].values[0], 0.2)
        self.assertGreater(report_overall["iou"].values[1], 0.3)


if __name__ == '__main__':
    unittest.main()
