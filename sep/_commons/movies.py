import traceback

import cv2
import numpy as np
import pathlib
import typing as t

from sep._commons import imgutil
from sep._commons.utils import *


class StreamReader:
    def __init__(self, input_string)
        self.input_string = str(input_string)
        self.frame_num = None
        self.current_frame = 0

    def __iter__(self):
        return self.read_samples(self.frame_rate)

    def read_samples(self, sampling_framerate: float) -> t.Iterable[np.ndarray]:
        current_time = 0
        next_sample_time = 0
        sampling_interval = 1.0 / sampling_framerate
        self.reader.set(cv2.CAP_PROP_POS_FRAMES, 0)
        for i in range(self.frame_num):
            res, image = self.reader.read()
            if not res:
                print(f"Failed to get frame nr {i}.")
            if next_sample_time <= current_time:
                yield image[..., ::-1]  # make it RGB
                next_sample_time += sampling_interval
            current_time += self.frame_interval

    def pos_samples(self, sampling_framerate: float) -> t.List[int]:
        res = []
        current_time = 0
        next_sample_time = 0
        sampling_interval = 1.0 / sampling_framerate
        for i in range(self.frame_num):
            if next_sample_time <= current_time:
                res.append(i)
                next_sample_time += sampling_interval
            current_time += self.frame_interval
        return res

    def move_to_item(self, item):
        if self.current_frame > item or item > self.current_frame + 500:
            self.reader.set(cv2.CAP_PROP_POS_FRAMES, item)
        else:
            while self.current_frame < item:
                self.reader.grab()
                self.current_frame += 1

    def __getitem__(self, item):
        self.move_to_item(item)
        res, image = self.reader.read()
        if not res:
            print(f"Failed to get frame nr {item}.")
        self.current_frame = item + 1
        return image[..., ::-1]

    @property
    def shape(self):
        return self.frame_h, self.frame_w

    def __len__(self):
        return self.frame_num

    def __enter__(self):
        assert self.input_string.startswith("http") or os.path.isfile(self.input_string), \
            f"File {self.input_string} does not exist."
        self.reader = cv2.VideoCapture(self.input_string)
        self.frame_rate = int(self.reader.get(cv2.CAP_PROP_FPS))
        self.frame_interval = 1.0 / self.frame_rate
        self.frame_h = int(self.reader.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.frame_w = int(self.reader.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.frame_num = int(self.reader.get(cv2.CAP_PROP_FRAME_COUNT))
        return self

    def __exit__(self, exc_type, exc_value, tb):
        if exc_type is not None:
            traceback.print_exception(exc_type, exc_value, tb)
        self.close()

    def close(self):
        if self.reader is not None:
            self.reader.release()


class VideoWriter:
    def __init__(self, output_path: t.Union[str, pathlib.Path], output_shape=None, fps=None,
                 related_reader: StreamReader = None, encoding='mp4v'):
        """
        Args:
            output_path: path to the output file
            output_shape: (Y,X) shape of the imagery, ignored when related reader provided
            fps: frame rate of the output video, ignored when related reader provided
            related_reader: reader where the processed data will come from
            encoding: the desired encoding of the output file
        """
        assert related_reader is not None or \
               (len(output_shape) == 2 or len(output_shape) == 3 and output_shape[2] == 3,
                "Incorrect shape " + str(output_shape))

        self.encoding = encoding
        self.frames_num = 0
        if related_reader is None:
            assert fps is not None and output_shape is not None
            self.frame_rate = fps
            self.frame_h = output_shape[0]
            self.frame_w = output_shape[1]
        else:
            self.frame_rate = int(related_reader.frame_rate)
            self.frame_h, self.frame_w = related_reader.shape
        self.output_path = str(output_path)

    def add(self, image: np.ndarray, accept_bool=False, accept_float=False):
        """
        Args:
            image: RGB or single channel image
            accept_float: convert float 0-1 to uint8
            accept_bool: convert bool to uint8
        """
        assert accept_bool or not image.dtype == np.bool
        assert accept_float or not image.dtype == np.float
        assert_arg(image.shape[:2] == self.shape, f"image.shape not compatible with {self.shape}")

        bgr_array = imgutil.make_rgb(image)[..., ::-1]
        self.video_writer.write(bgr_array)

    @property
    def shape(self):
        return self.frame_h, self.frame_w

    def __enter__(self):
        self.video_writer = cv2.VideoWriter(self.output_path,
                                            cv2.VideoWriter_fourcc(*self.encoding),
                                            self.frame_rate,
                                            (self.frame_w, self.frame_h))
        return self

    def __exit__(self, exc_type, exc_value, tb):
        if exc_type is not None:
            traceback.print_exception(exc_type, exc_value, tb)
        self.close()

    def close(self):
        self.video_writer.release()
