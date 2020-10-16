import os
from tqdm import tqdm

from sep.loaders.loader import Loader
from sep.producers.producer import Producer
from sep.savers.saver import Saver


def process(data_loader: Loader, producer: Producer, result_saver: Saver,
            output_root,
            verbose=1):
    if verbose:
        print(f"Processing by {producer} on data from '{data_loader}'.")
        print(f"Results will be saved at {output_root} using {result_saver}.")
        print(f"There are {len(data_loader)} images to process.")

    result_saver.set_output(output_root, data_loader)
    os.makedirs(output_root, exist_ok=True)

    for i in tqdm(range(len(data_loader)), producer.name):
        image = data_loader.load_image(i)
        tag = data_loader.load_tag(i)

        segment, segment_tag = producer.calculate(image, tag)
        result_saver.save_result(i, segment)
        result_saver.save_tag(i, input_tag=tag, result_tag=segment_tag)
    result_saver.close()

    return producer
