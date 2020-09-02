import numpy as np
import numpy.testing as nptest

import sep.inspect.regions
import tests.testbase


class TestRegions(tests.testbase.TestBase):
    def test_overlay_single(self):
        random_soup = np.random.random((10, 10, 3)) / 2.0
        empty_mask = np.zeros(random_soup.shape[:-1], dtype=np.uint8)

        overlay = sep.inspect.regions.overlay_region(random_soup, empty_mask)
        are_greys = overlay[...,0] == overlay[...,1]
        self.assertEqual(np.count_nonzero(are_greys), overlay.size / 3)

        full_mask = np.ones(random_soup.shape[:-1], dtype=np.uint8)
        overlay = sep.inspect.regions.overlay_region(random_soup, full_mask)
        are_greys = overlay[..., 0] == overlay[..., 1]
        self.assertEqual(np.count_nonzero(are_greys), 0)

    def test_overlay_multiple(self):
        whiteness = np.ones((10, 10, 3)) * 70
        half_mask = np.zeros(whiteness.shape[:-1], dtype=np.uint8)
        half_mask[0:5] = 1
        second_mask = np.zeros(whiteness.shape[:-1], dtype=np.uint8)
        second_mask[4:10] = 1

        overlay, legend = sep.inspect.regions.overlay_regions(whiteness, [half_mask, second_mask], regions_names=None)
        pass

