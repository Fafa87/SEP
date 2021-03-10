from sep._commons.utils import *
from tests.testbase import TestBase


class TestUtils(TestBase):
    def test_time_to_sec(self):
        self.assertEqual(15, time_to_sec("15"))
        self.assertEqual(75, time_to_sec("1:15"))
        self.assertEqual(75, time_to_sec("01:15"))
        self.assertEqual(7275, time_to_sec("02:01:15"))

    def test_pick_subset(self):
        dictionary = {'a': 1, 'b': 3, 'c': 4}
        res = subset(dictionary, ['a'])
        self.assertDictEqual(res, {'a': 1})
        res = subset(dictionary, ['a', 'c'])
        self.assertDictEqual(res, {'a': 1, 'c': 4})
        res = subset(dictionary, ['b', 'c'])
        self.assertDictEqual(res, {'b': 3, 'c': 4})
