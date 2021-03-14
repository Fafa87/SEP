from sep._commons.imgutil import *
from tests.testbase import TestBase


class TestImgUtil(TestBase):
    def test_make_2d(self):
        with self.assertRaises(ValueError):
            image_4d = np.random.random((2, 2, 2, 2))
            make_2d(image_4d)

        image_2d = self.random_uint((20, 20))
        self.assertEqual(2, image_2d.ndim)
        res = make_2d(image_2d)
        self.np_assert_equal(res, image_2d)

        image_2d_rgb = make_rgb(image_2d)
        self.assertEqual(3, image_2d_rgb.ndim)
        res = make_2d(image_2d_rgb)
        self.np_assert_equal(res, image_2d)

        image_3d = self.random_rgb((20, 20))
        res = make_2d(image_3d, strict_duplication=False)  # this is possible, resulting is mean
        self.np_assert_equal(res.ndim, 2)

        with self.assertRaises(ValueError):
            make_2d(image_3d, strict_duplication=True)

