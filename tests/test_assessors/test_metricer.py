import unittest

import numpy as np
import numpy.testing as nptest

from sep.assessors.metricer import Metricer
from sep.assessors.metrics import IouMetric
from sep.assessors.regions import Region, EntireRegion


class TestMetrics(unittest.TestCase):
    def test_iou(self):
        iou = IouMetric()
        blob_1 = np.zeros((10, 10))
        blob_1[0:5, 0:10] = 1

        blob_2 = np.zeros((10, 10))
        blob_2[4:6, 0:5] = 1

        metric = iou.calculate(blob_2, blob_1)
        self.assertAlmostEqual(5.0 / (50 + 5), metric, places=5)


class TestRegions(unittest.TestCase):
    def test_entire(self):
        entire_region = EntireRegion()
        blob_1 = np.zeros((10, 10))
        blob_1[0:5, 0:10] = 1

        blob_2 = np.zeros((10, 10))
        blob_2[4:6, 0:5] = 1

        self.assertEqual("Entire image", entire_region.name)
        nptest.assert_equal(blob_1, entire_region.regionize(blob_2, blob_1))


class TestMetricer(unittest.TestCase):
    class DummyRegion(Region):
        def regionize(self, ground_truth, mask):
            return ground_truth.astype(np.bool) & mask.astype(np.bool)

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


if __name__ == '__main__':
    unittest.main()
