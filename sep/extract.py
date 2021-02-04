import fire
import shutil
from tqdm import tqdm

import sep.loaders
from sep._commons.utils import *
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


def extract_from_youtube_to_images(url_list_path, output_root, quality="720p"):
    """
    Extract image frames from youtube videos defined in the url_list_path file.
    File format is:
    <url>;<start_time>;<end_time>;<frames_numbers>;<optional_tags>
    <start_time> / <end_time> = <min>:<sec>
    <optional_tags> = <tag_name>:<tag_value>;<optional_tags>
    Args:
        url_list_path: path to the file with youtube videos to extract
        output_root: directory where the image frames will be saved
        quality: string description
    """
    url_samples = [l.strip() for l in open(url_list_path, "r").readlines()]

    # Parse url sample.
    extract_samples = []
    for url_sample in url_samples:
        tokens = [s.strip() for s in url_sample.split(";")]
        sample = {'url': tokens[0], 'start_time': tokens[1], 'end_time': tokens[2], 'frames_numbers': int(tokens[3])}

        # parse tags
        tags = {}
        for t in tokens[4:]:
            key, value = map(str.strip, t.split(":"))
            tags[key] = value

        sample['start_time'] = time_to_sec(sample['start_time'])
        sample['end_time'] = time_to_sec(sample['end_time'])
        sample['tags'] = tags
        extract_samples.append(sample)

    # Saving from youtube.
    saver = sep.savers.ImagesSaver()
    with sep.loaders.YoutubeLoader(quality) as youtube_loader:
        for sample in tqdm(extract_samples, "Preparing extraction plan"):
            url = sample['url']
            selector = sep.loaders.FrameByIntervalSelector(frames_to_extract=sample['frames_numbers'],
                                                           interval_start_time=sample['start_time'],
                                                           interval_end_time=sample['end_time'])
            youtube_loader.add_url(url, selector, user_info=sample['tags'])
        extract_to_images(youtube_loader, saver, output_root, remove_existing=True)


if __name__ == '__main__':
    fire.Fire()
