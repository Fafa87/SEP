import unittest

import sep.extract
import sep.loaders
import sep.process
import sep.savers
import tests.testbase


class TestExtract(tests.testbase.TestBase):
    def test_extract_from_movie(self):
        output_dir = self.create_temp_dir()
        saver = sep.savers.ImagesSaver()
        with sep.loaders.MoviesLoader.from_tree(self.root_test_dir("input/reptiles"),
                                                framerate=5, clips_len=1, clips_skip=10) as movies_loader:
            self.assertEqual(9, len(movies_loader.list_images_paths()))
            loader = sep.extract.extract_to_images(movies_loader, saver, output_dir, remove_existing=True)
            self.assertEqual(9, len(loader.list_images()))

        extracted_loader = sep.loaders.ImagesLoader.from_tree(output_dir)
        self.assertEqual(9, len(extracted_loader.list_images()))

    @unittest.skip("perf_test")
    def test_extract_from_movie_speed(self):
        output_dir = self.create_temp_dir()
        saver = sep.savers.ImagesSaver(image_format='.bmp')
        with sep.loaders.MoviesLoader.from_tree(r"D:\Filmy i zdjęcia",
                                                framerate=None, clips_len=1, clips_skip=2) as movies_loader:
            sep.extract.extract_to_images(movies_loader, saver, output_dir, remove_existing=True)

    @unittest.skip("internet")
    def test_extract_from_youtube(self):
        output_dir = self.create_temp_dir()
        saver = sep.savers.ImagesSaver()
        with sep.loaders.YoutubeLoader(['https://www.youtube.com/watch?v=_cLFseR-S50'], '720p',
                                       framerate=1, clips_len=1, clips_skip=60) as youtube_loader:
            self.assertEqual(5, len(youtube_loader.list_images_paths()))
            loader = sep.extract.extract_to_images(youtube_loader, saver, output_dir, remove_existing=True)
            self.assertEqual(5, len(loader.list_images()))

        extracted_loader = sep.loaders.ImagesLoader.from_tree(output_dir)
        self.assertEqual(5, len(extracted_loader.list_images()))


if __name__ == '__main__':
    unittest.main()
