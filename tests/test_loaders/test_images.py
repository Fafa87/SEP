import numpy.testing as nptest
import os
import unittest
from pathlib import Path

from sep.loaders.images import ImagesLoader
from tests.testbase import TestBase


class TestImagesLoader(TestBase):
    def test_loading(self):
        loader = ImagesLoader.from_tree(self.root_test_dir("input/basics/lights"))
        self.assertEqual(2, len(loader))
        self.assertEqual(['lights01', 'lights02'], loader.input_order)

        input_data_02_by_id = loader.load_image(1)
        input_data_02_by_name = loader.load_image('lights02')
        nptest.assert_equal(input_data_02_by_id, input_data_02_by_name)

        tag_02 = loader.load_tag('lights02')
        self.assertEqual("lights02", tag_02["id"])
        self.assertEqual("thenet", tag_02["source"])
        non_existing_tag10 = loader.load_tag('lights10')
        self.assertEqual("lights10", non_existing_tag10["id"])
        self.assertNotIn("source", non_existing_tag10)

        annotation_1 = loader.load_annotation(0)
        self.assertEqual(annotation_1.shape, input_data_02_by_id.shape[:2])
        self.assertEqual(255, annotation_1.max())

        tag_1 = loader.load_tag(0)
        self.assertEqual(0, tag_1["id"])  # TODO RETHINK default tags mirror exact call

    def test_get_element(self):
        loader = ImagesLoader.from_tree(self.root_test_dir("input/basics/lights"))
        second_elem = loader[1]
        self.assertIn("image", second_elem)
        self.assertIn("annotation", second_elem)
        self.assertIn("tag", second_elem)

    def test_iterate_through(self):
        loader = ImagesLoader.from_tree(self.root_test_dir("input/basics/lights"))
        data = [p for p in loader]
        self.assertEqual(2, len(data))
        second_elem = data[1]
        self.assertIn("image", second_elem)
        self.assertIn("annotation", second_elem)
        self.assertIn("tag", second_elem)

    def test_relative(self):
        loader = ImagesLoader.from_tree(self.root_test_dir("input/basics"))
        data_names = loader.list_images()
        self.assertEqual(5, len(data_names))
        self.assertEqual("human_1", data_names[0])
        self.assertEqual(os.path.join("humans", "human_1.tif"), loader.get_relative_path(0))
        self.assertEqual(os.path.join("humans", "human_1.tif"), loader.get_relative_path("human_1"))

    def test_listing_save(self):
        loader = ImagesLoader.from_tree(self.root_test_dir("input/basics"))
        data_names = loader.list_images()
        self.assertEqual(5, len(data_names))

        listing_path = self.add_temp("loader_listing.txt")
        loader.save(listing_path, add_tag_path=False)

        # check that there are 5 lines and that they point to the actual files
        with open(listing_path, "r") as listing_file:
            listing_lines = listing_file.readlines()
        self.assertEqual(5, len(listing_lines))
        self.assertEqual(f"{Path('humans/human_1.tif')}, {Path('humans/human_1_gt.png')}",
                         listing_lines[0].strip())

        loader.save(listing_path, add_tag_path=True)
        # now it has tag files (at least expected)
        with open(listing_path, "r") as listing_file:
            listing_lines = listing_file.readlines()
        self.assertEqual(f"{Path('humans/human_1.tif')}, {Path('humans/human_1_gt.png')}, {Path('humans/human_1.json')}",
                         listing_lines[0].strip())

    def test_listing_filter_load(self):
        loader = ImagesLoader.from_tree(self.root_test_dir("input/basics"))
        self.assertEqual(5, len(loader.list_images()))
        names = loader.list_images()
        loader.filter_files([0, 'human_3', 4])
        with self.assertRaises(ValueError):
            loader.filter_files([0, 'my_image'])
        self.assertEqual(3, len(loader.list_images()))
        self.assertEqual(names[::2], loader.list_images())

        listing_file = self.add_temp("loader_listing.txt")
        loader.save(listing_file, add_tag_path=False)

        # check that there are 3 lines and that they point to the actual files
        loader_reloaded = ImagesLoader.from_listing(self.root_test_dir("input/basics"), filepath=listing_file)
        self.assertEqual(3, len(loader_reloaded.list_images()))
        self.assertEqual(loader.list_images(), loader_reloaded.list_images())

    def test_listing_load_partial_gt(self):
        with self.create_temp("loader_listing.txt") as listing_file:
            listing_file.writelines(f"{Path('humans/human_1.tif')}, {Path('humans/human_1_gt.png')}\n")
            listing_file.writelines(f"{Path('humans/human_2.tif')}, \n")
            # TODO there should be difference between not known ground truth path and non existing file at known position
            # TODO at the moment there is none - there is no trace of what was in the listing file

        loader_proper = ImagesLoader.from_listing(self.root_test_dir("input/basics"), filepath="loader_listing.txt")
        self.assertEqual(2, len(loader_proper))
        elem_1 = loader_proper[0]
        self.assertIsNotNone(elem_1['image'])
        self.assertIsNotNone(elem_1['annotation'])
        elem_2 = loader_proper[1]
        self.assertIsNotNone(elem_2['image'])
        self.assertIsNone(elem_2['annotation'])

    def test_listing_load_missing_image(self):
        with self.create_temp("loader_listing.txt") as listing_file:
            listing_file.writelines(f"{Path('humans/human_1.tif')}, {Path('humans/human_1_gt.png')}\n")
            listing_file.writelines(f"{Path('humans2/human2_2.tif')}, {Path('humans2/human2_2_gt.png')}\n")

        # always fail for missing image
        with self.assertRaises(ValueError):
            ImagesLoader.from_listing(self.root_test_dir("input"), filepath="loader_listing.txt")

    def test_listing_load_missing_annotation_tag(self):
        with self.create_temp("loader_listing.txt") as listing_file:
            listing_file.writelines(f"{Path('lights/lights01.tif')},\n")
            listing_file.writelines(f"{Path('lights/lights02.tif')}\n")
            listing_file.writelines(f"{Path('humans/human_1.tif')}, {Path('humans/human_1_gt.png')}\n")
            listing_file.writelines(
                f"{Path('humans/human_2.tif')}, {Path('humans/human_2_gt_extra.png')}, {Path('humans/human_2_gt_extra.json')}\n")

        # this should work - TODO potentially log warnings
        loader = ImagesLoader.from_listing(self.root_test_dir("input/basics"), filepath="loader_listing.txt")
        self.assertEqual(4, len(loader.list_images()))
        self.assertIsNone(loader['lights01']['annotation'])
        self.assertIsNone(loader['lights02']['annotation'])
        self.assertIsNotNone(loader['human_1']['annotation'])
        self.assertIsNone(loader['human_2']['annotation'])
        self.assertNotIn("source", loader['human_2']['tag'])

    def test_listing_load_from_actual_file(self):
        loader = ImagesLoader.from_listing(self.root_test_dir("input/basics"),
                                           filepath=self.root_test_dir("input/picky_images.txt"))
        images_names = loader.list_images()
        expected_names = ['human_1', 'human_3', 'lights01', 'lights02']
        self.assertEqual(expected_names, images_names)

        data = list(loader)
        self.assertEqual(4, len(data))
        for d in data[:3]:
            self.assertIsNotNone(d['image'])
            self.assertGreater(d['image'].shape[0], 0)
            self.assertIsNotNone(d['annotation'])
            self.assertGreater(d['annotation'].shape[0], 0)

        # first one has also tag json file
        self.assertIn("source", data[0]['tag'])
        self.assertIsNotNone(data[0]['tag'])

        # second does not have json file
        self.assertNotIn("source", data[1]['tag'])
        self.assertIsNotNone(data[1]['tag'])

        # last one does not have annotation specified
        self.assertIsNotNone(data[3]['image'])
        self.assertGreater(data[3]['image'].shape[0], 0)
        self.assertIsNone(data[3]['annotation'])
        self.assertNotIn("source", data[3]['tag'])
        self.assertIsNotNone(data[3]['tag'])

    def test_extended_ids(self):
        loader = ImagesLoader.from_tree(self.root_test_dir("input/basics"))
        first_image = loader.list_images()[0]
        self.assertEqual("human_1", first_image)
        first_path = loader.list_images_paths()[0]
        self.assertEqual("human_1", loader.path_to_id(first_path))

        loader.extended_ids = True
        self.assertEqual("humans/human_1", loader.path_to_id(first_path))

    def test_use_extended_ids_when_necessary(self):
        loader = ImagesLoader.from_tree(self.root_test_dir("input/brightfield"), annotation_extension=".tif")
        image_names = loader.list_images()
        self.assertEqual(2, len(image_names))
        self.assertEqual("view1/BF_frame001", image_names[0])
        self.assertEqual("view2/BF_frame001", image_names[1])
        # make sure that gt is read despite being tif
        self.assertIsNotNone(loader.load_annotation(0))
        self.assertIsNotNone(loader.load_annotation(1))

    def test_custom_annotation_mapping(self):
        loader = ImagesLoader.from_tree(self.root_test_dir("input/brightfield/view1"),
                                        annotation_suffix=None,
                                        annotation_for_image_finder=lambda p: p.stem + "_gt.tif")
        # Find annotation to the input image but assumed that annotation is a sample on her own.
        image_names = loader.list_images()
        self.assertEqual(2, len(image_names))
        self.assertEqual("BF_frame001", image_names[0])
        self.assertEqual("BF_frame001_gt", image_names[1])
        self.assertIsNotNone(loader.load_annotation(0))
        self.assertIsNone(loader.load_annotation(1))

        loader = ImagesLoader.from_tree(self.root_test_dir("input/brightfield/view1"),
                                        annotation_suffix=None,
                                        annotation_checker=lambda p: p.stem.endswith("_gt"),
                                        annotation_for_image_finder=lambda p: p.stem + "_gt.tif")
        # Now finds proper dataset.
        image_names = loader.list_images()
        self.assertEqual(1, len(image_names))
        self.assertEqual("BF_frame001", image_names[0])
        self.assertIsNotNone(loader.load_annotation(0))





        pass


if __name__ == '__main__':
    unittest.main()
