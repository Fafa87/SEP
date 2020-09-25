from matplotlib import pyplot as plt, patches as mpatches

import skimage
from skimage.color.colorlabel import DEFAULT_COLORS


def overlay(image, labels):
    return skimage.color.label2rgb(labels, image, colors=DEFAULT_COLORS, bg_label=0)


def show_with_legend(image, legend, title="", scale=None):
    scale = scale or 30
    shape_ratio = image.shape[0] / image.shape[1]

    fig, ax = plt.subplots(1, 1, figsize=(scale, scale * shape_ratio))
    ax.set_aspect("auto")
    ax.set_title(title)

    legend_patches = [mpatches.Patch(color=colour, label=name) for name, colour in legend]
    plt.legend(handles=legend_patches, prop={'size': 16})

    ax.imshow(image)
    plt.close(fig)
    return fig
