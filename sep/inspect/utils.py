import numpy as np
import os
import sys
from IPython.display import Markdown, display, HTML
from matplotlib import pyplot as plt
from matplotlib.colors import ListedColormap, NoNorm
from pathlib import Path

random_colormap = ListedColormap([(0, 0, 0)] + list(np.random.rand(20000, 3)))


def add_root_to_path(steps_up):
    root_dir = Path(__file__)
    for _ in range(steps_up):
        root_dir = root_dir.parent

    if root_dir not in sys.path:
        sys.path.append(str(root_dir))
    return root_dir


def pick_path(paths):
    correct_paths = [p for p in paths if os.path.exists(p)]
    if len(correct_paths) > 1:
        raise Exception("More than one existing path to choose.")
    elif len(correct_paths) == 0:
        raise Exception("No path exists.")
    return correct_paths[0]


def info(array, name=""):
    print(name, type(array))
    info_string = f"Shape: {array.shape}, Type: {array.dtype}, Min-max: {array.min(), array.max()}"
    info_string += f", Mean: {array.mean()}"
    print(info_string)


def show(*args, **kwargs):
    show_all(1, len(args), *args, **kwargs)


def show_all(rows, cols, *args, display_now=True, **kwargs):
    """
    Presents given arrays in form of grid as matplotlib figure.
    Args:
        rows: number of rows to show.
        cols: number of columns to show.
        *args: list of numpy arrays to show
        display_now: should the figure be displayed immediately
        **kwargs:
            - scale: define figsize
            - cmap: value mapping for each or every array
                if 'rand' then no normalization and random int to RGB mapping used
                else it is just passed to imshow
    Returns:
        matplotlib figure to show in notebook
    """
    scale = 30
    if 'scale' in kwargs:
        scale = kwargs['scale']

    subtitles = kwargs.get("titles", [""])

    gray_cmaps = ['gray']
    random_map = random_colormap
    normalization = [True]
    if 'cmap' in kwargs:
        gray_cmap_params = kwargs['cmap'].split(',')
        gray_cmaps = []
        normalization = []
        for m in gray_cmap_params:
            is_rand = m.strip() == 'rand'
            normalization.append(not is_rand)
            if is_rand:
                gray_cmaps.append(random_map)
            else:
                gray_cmaps.append(m)

    shape_ratio = args[0].shape[0] / args[0].shape[1]
    fig, axes = plt.subplots(rows, cols, figsize=(scale * cols, scale * rows * shape_ratio))
    fig.subplots_adjust(wspace=0.01, hspace=0.01)
    plt.subplots_adjust(wspace=0.01, hspace=0.01)
    for i in range(rows * cols):
        array = args[i] if len(args) > i else np.zeros(args[0].shape)
        if rows == 1 and cols == 1:
            ax = axes
        else:
            ax = axes[i] if rows == 1 or cols == 1 else axes[i // cols][i % cols]

        sub_ix = i
        subtitle = ""
        if len(subtitles) <= i:
            sub_ix = i % cols

        if len(subtitles) > sub_ix:
            subtitle = subtitles[sub_ix]

        ax.set_aspect("auto")
        ax.set_title(subtitle)
        if len(array.shape) == 3:
            if array.dtype == np.uint32 or array.dtype == np.uint16:
                array = (array / np.iinfo(array.dtype).max * 255).astype(np.uint8)
            ax.imshow(array)
        else:
            map_id = i % len(gray_cmaps)
            if normalization[map_id]:
                ax.imshow(array, cmap=gray_cmaps[map_id])
            else:
                ax.imshow(array, norm=NoNorm(), cmap=gray_cmaps[map_id])

    plt.close(fig)
    if display_now:
        display(fig)
    return fig


def printmd(*text):
    display(Markdown(" ".join([str(t) for t in text])))


def display_width(size_perc):
    display(HTML("<style>.container { width:{0}% !important; }</style>".format(size_perc)))
