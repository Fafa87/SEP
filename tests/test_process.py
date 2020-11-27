import unittest

import sep.loaders.images
import sep.process
import sep.producers.producer
import sep.savers.images
import tests.testbase


class TestProcess(tests.testbase.TestBase):
    class Threshold(sep.producers.ImagesProducer):
        def __init__(self, name, channel, cache_root, threshold=200):
            super().__init__(name=name, cache_root=cache_root)
            self.threshold = threshold
            self.channel = channel

        def segmentation(self, image, image_tag):
            return image[..., self.channel] > self.threshold

    def test_process_images(self):
        output_dir = self.create_temp_dir()
        images_loader = sep.loaders.ImagesLoader.from_tree(self.root_test_dir("input/basics/lights"))
        images_saver = sep.savers.ImagesSaver()
        producer_red = self.Threshold("Red", 0, self.create_temp_dir())

        sep.process.process(images_loader, producer_red, images_saver, output_dir)
        output_loader = sep.loaders.images.ImagesLoader.from_tree(output_dir)
        self.assertEqual(len(images_loader), len(output_loader))

    def test_process_movies_frames(self):
        output_dir = self.create_temp_dir()
        movies_loader = sep.loaders.MoviesLoader.from_tree(self.root_test_dir("input/reptiles"),
                                                 framerate=1, clips_skip=0, clips_len=1)
        images_saver = sep.savers.ImagesSaver()
        producer_red = self.Threshold("Red", 0, self.create_temp_dir())

        sep.process.process(movies_loader, producer_red, images_saver, output_dir)
        output_loader = sep.loaders.images.ImagesLoader.from_tree(output_dir)
        self.assertEqual(len(movies_loader), len(output_loader))

    def test_process_movies_files(self):
        output_dir = self.create_temp_dir()
        with sep.loaders.MoviesLoader.from_tree(self.root_test_dir("input/reptiles"),
                                      framerate=1, clips_skip=0, clips_len=1) as movies_loader:
            movie_saver = sep.savers.MoviesSaver()
            movie_saver.set_output(output_dir, movies_loader)
            producer_red = self.Threshold("Red", 0, self.create_temp_dir(), threshold=30)
            sep.process.process(movies_loader, producer_red, movie_saver, output_dir)

        with sep.loaders.MoviesLoader.from_tree(output_dir,
                                      framerate=1, clips_skip=0, clips_len=1) as output_loader:
            self.assertEqual(len(movies_loader), len(output_loader))
            self.assertEqual(movies_loader.list_movies(), output_loader.list_movies())
            self.assertEqual(len(movies_loader.list_images()), len(output_loader.list_images()))


if __name__ == '__main__':
    unittest.main()
