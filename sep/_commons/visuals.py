import skimage
from matplotlib import pyplot as plt, patches as mpatches
from skimage.color.colorlabel import DEFAULT_COLORS

import sep._commons.imgutil


def overlay(image, labels):
    return skimage.color.label2rgb(labels, image, colors=DEFAULT_COLORS, bg_label=0)


def overlay_prediction(image, prediction, cmap='gnuplot2', pred_alpha=0.5):
    """
    Args:
        image: grayscale or rgb image
        prediction: float np array
        cmap: name of the cmap to use
        pred_alpha: image colour mapped image blending (1 is show only prediction)

    Returns:
        RGB np array
    """
    if image.ndim == 2:
        image = skimage.color.gray2rgb(image)
    cm = plt.get_cmap(cmap)
    prediction_rgb = cm(prediction)[..., 0:3] * 255
    return sep._commons.imgutil.make_rgb(pred_alpha * prediction_rgb + (1 - pred_alpha) * image)


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
