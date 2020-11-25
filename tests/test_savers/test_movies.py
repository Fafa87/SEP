import os
import unittest

from sep.loaders import MoviesLoader
from sep.savers import MoviesSaver
from tests.testbase import TestBase


class TestMoviesSaver(TestBase):
    def test_saving_in_hierarchy(self):
        with MoviesLoader.from_tree(self.root_test_dir("input"), framerate=5, clips_len=1, clips_skip=10) as movies_loader:
            temp_dir = self.create_temp_dir()
            movies = movies_loader.list_movies()
            self.assertEqual(3, len(movies))
            self.assertEqual(10, len(movies_loader.list_images()))
            self.assertEqual("Dragon - 32109", movies[1])
            movies_loader.load_image(0)

            with MoviesSaver(temp_dir, loader=movies_loader) as saver:
                sample_res_1 = self.random_rgb((360, 640))
                sample_tag_1 = {"movie_id": "dragon_1", "movie_source": "pixabay", "movie_type": "flying"}
                saver.save_result(0, sample_res_1)
                saver.save_tag(0, sample_tag_1, result_tag={'seg_name': 'fast'})
                saver.save_result(8, sample_res_1)
                saver.save_tag(8, sample_tag_1, result_tag={'seg_name': 'slow'})

            self.assertTrue(os.path.isfile(os.path.join(temp_dir, "Dinosaur - 1438.mp4")))
            self.assertTrue(os.path.isfile(os.path.join(temp_dir, "Dragon - 32109.mp4")))

        with MoviesLoader.from_tree(temp_dir, framerate=5, clips_len=1, clips_skip=0) as reload_movies:
            self.assertEqual(2, len(reload_movies.list_movies()))
            self.assertEqual(2, len(reload_movies.list_images()))
            # TODO check tag if it is stripped of the movie per movie file
            # TODO check tag read - it should be similar to the saved one


if __name__ == '__main__':
    unittest.main()
