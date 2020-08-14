import unittest

import numpy as np
import numpy.testing as nptest

from sep.assessors.metricer import Metricer
from sep.assessors.metrics import IouMetric
from sep.assessors.regions import Region, EntireRegion


class TestProducer(unittest.TestCase):
    def test_simple_producer(self):
        iou = IouMetric()
        blob_1 = np.zeros((10, 10))
        blob_1[0:5, 0:10] = 1

        blob_2 = np.zeros((10, 10))
        blob_2[4:6, 0:5] = 1

        metric = iou.calculate(blob_2, blob_1)
        self.assertAlmostEqual(5.0 / (50 + 5), metric, places=5)


if __name__ == '__main__':
    unittest.main()
