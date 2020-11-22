import fire
import os
import shutil
from tqdm import tqdm

import sep.loaders
from sep.loaders.loader import Loader
from sep.savers.saver import Saver


def extract_to_images(data_loader: Loader, data_saver: Saver,
                      output_root,
                      remove_existing=False,
                      verbose=1):
    if verbose:
        print(f"Extracting images from {data_loader}.")
        print(f"Results will be saved at {output_root} using {data_saver}.")
        print(f"There are {len(data_loader)} images to process.")

    data_saver.set_output(output_root, data_loader)
    if remove_existing and os.path.exists(output_root):
        shutil.rmtree(output_root)
    os.makedirs(output_root)

    for i in tqdm(range(len(data_loader)), "Extracting images"):
        image = data_loader.load_image(i)
        tag = data_loader.load_tag(i)

        data_saver.save_result(i, image)
        data_saver.save_tag(i, tag, result_tag={})
    data_saver.close()

    extracted_loader = sep.loaders.ImagesLoader.from_tree(output_root)
    if verbose:
        print(f"Extracted {len(data_loader)} images and loader found {len(extracted_loader)} of them.")
    if len(data_loader) != len(extracted_loader):
        print("Different count of the extracted and reloaded images!")
    return extracted_loader


def extract_from_movies_to_images(movies_root, output_root):
    movies_loader = sep.loaders.MoviesLoader(movies_root, framerate=None, clips_skip=0, clips_len=10000000, verbose=1)
    saver = sep.savers.ImagesSaver(output_root, movies_loader)
    extract_to_images(movies_loader, saver, output_root)


if __name__ == '__main__':
    fire.Fire()
