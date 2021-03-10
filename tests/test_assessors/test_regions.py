import numpy as np
import numpy.testing as nptest
import unittest

from sep.assessors.regions import EntireRegion, EdgesRegion, DetailsRegion
from tests.testbase import TestBase


class TestRegions(TestBase):
    def test_entire(self):
        entire_region = EntireRegion()
        blob_1 = np.zeros((10, 10))
        blob_1[0:5, 0:10] = 1

        blob_2 = np.zeros((10, 10))
        blob_2[4:6, 0:5] = 1

        self.assertEqual("Entire image", entire_region.name)
        nptest.assert_equal(blob_1, entire_region.regionize(blob_2, blob_1))

    def test_edges_smoke(self):
        edges_region_int = EdgesRegion(2)
        blob_1 = np.zeros((10, 10))
        blob_1[0:5, 0:10] = 1

        blob_2 = np.zeros((10, 10))
        blob_2[4:6, 0:5] = 1

        some_region = edges_region_int.regionize(blob_2, blob_1)

        edges_region_float = EdgesRegion(0.2)
        some_region = edges_region_float.regionize(blob_2, blob_1)

    def test_details_smoke(self):
        details_region_int = DetailsRegion(2)
        blob_1 = np.zeros((10, 10))
        blob_1[0:5, 0:10] = 1

        blob_2 = np.zeros((10, 10))
        blob_2[4:6, 0:5] = 1

        some_region = details_region_int.regionize(blob_2, blob_1)

        details_region_float = DetailsRegion(0.2)
        some_region = details_region_float.regionize(blob_2, blob_1)

    def test_expressions(self):
        edges_region_int = EdgesRegion(1)
        blob_1 = np.zeros((10, 10))
        blob_1[0:5, 0:10] = 1

        blob_2 = np.zeros((10, 10))
        blob_2[4:6, 0:5] = 1

        non_edge = ~edges_region_int
        regionized_region_edge = edges_region_int.regionize(blob_2, blob_1)
        regionized_region_non_edge = non_edge.regionize(blob_2, blob_1)
        nptest.assert_equal(regionized_region_edge, regionized_region_non_edge == 0)

        region_edge = edges_region_int.extract_region(blob_2)
        region_non_edge = non_edge.extract_region(blob_2)
        nptest.assert_equal(region_edge, region_non_edge == 0)

        bigger_edges_region_int = EdgesRegion(2)
        or_region = non_edge | bigger_edges_region_int
        and_region = non_edge & bigger_edges_region_int
        region_or = or_region.extract_region(blob_2)
        region_and = and_region.extract_region(blob_2)


if __name__ == '__main__':
    unittest.main()
