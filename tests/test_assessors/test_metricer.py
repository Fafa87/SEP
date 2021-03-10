import numpy as np
import numpy.testing as nptest
import unittest

from sep.assessors.metricer import Metricer
from sep.assessors.metrics import IouMetric
from sep.assessors.regions import Region
from tests.testbase import TestBase


class TestMetrics(TestBase):
    def test_iou(self):
        iou = IouMetric()
        blob_1 = np.zeros((10, 10))
        blob_1[0:5, 0:10] = 1

        blob_2 = np.zeros((10, 10))
        blob_2[4:6, 0:5] = 1

        metric = iou.calculate(blob_2, blob_1)
        self.assertAlmostEqual(5.0 / (50 + 5), metric, places=5)


class TestMetricer(TestBase):
    class DummyRegion(Region):
        def extract_region(self, ground_truth: np.ndarray) -> np.ndarray:
            return ground_truth.astype(np.bool)

    def test_basic_metricer(self):
        metricer = Metricer()
        blob_1 = np.zeros((10, 10))
        blob_1[0:5, 0:10] = 1

        blob_2 = np.zeros((10, 10))
        blob_2[4:6, 0:5] = 1

        empty_report = metricer.calculate_metrics(blob_2, blob_1)
        self.assertEqual(0, len(empty_report))

        iou_metric = IouMetric()
        metricer.metrics.append(iou_metric)
        report = metricer.calculate_metrics(blob_2, blob_1)
        self.assertEqual(1, len(report))
        nptest.assert_almost_equal([5.0 / (50 + 5)], report[iou_metric.name].values)
        nptest.assert_equal(["Entire image"], report["region"].values)

    def test_two_regions_metricer(self):
        metricer = Metricer()
        blob_1 = np.zeros((10, 10))
        blob_1[0:5, 0:10] = 1

        blob_2 = np.zeros((10, 10))
        blob_2[4:6, 0:5] = 1

        iou_metric = IouMetric()
        new_region = self.DummyRegion(name="Dummy")
        metricer.metrics.append(iou_metric)
        metricer.regions.append(new_region)

        report = metricer.calculate_metrics(blob_2, blob_1)
        self.assertEqual(2, len(report))
        nptest.assert_almost_equal([5.0 / (50 + 5), 5.0 / 50], report[iou_metric.name].values)
        nptest.assert_equal(["Entire image", "Dummy"], report["region"].values)

    def test_evaluate_image(self):
        metricer = Metricer()
        metricer.metrics.append(IouMetric())

        image = np.random.random((10, 10, 3))
        gt = np.zeros((10, 10), dtype=bool)
        gt[0:5, 0:10] = True
        seg = np.zeros((10, 10))
        seg[4:6, 0:5] = 1

        report = metricer.evaluate_image(image, tag={"id": "blobix"}, gt=gt,
                                         segment=seg, segment_tag={"name": "Resnet", "fps": 20})
        self.assertEqual(1, len(report))
        self.assertEqual(5, len(report.columns))
        nptest.assert_almost_equal(report["iou"].values, [5.0 / (50 + 5)])
        self.assertEqual(report["id"].values, ["blobix"])
        self.assertEqual(report["region"].values, ["Entire image"])
        self.assertEqual(report["seg_name"].values, ["Resnet"])
        self.assertEqual(report["seg_fps"].values, [20])


if __name__ == '__main__':
    unittest.main()
