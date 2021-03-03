import skimage
from matplotlib import pyplot as plt, patches as mpatches
from skimage.color.colorlabel import DEFAULT_COLORS

import sep._commons.imgutil as imgutil


def overlay(image, labels):
    return skimage.color.label2rgb(labels, image, colors=DEFAULT_COLORS, bg_label=0)


def overlay_as_rgb(image, red, green, blue, pred_alpha=0.75):
    """
    Args:
        image: grayscale or rgb image
        red: red channel
        green: green channel
        blue: blue channel
        pred_alpha: image colour mapped image blending (1 is show only prediction)

    Returns:
        RGB np array
    """
    # TODO check 0-1 vs 0-255, for now assume masks
    # TODO this should be rewritter using basic imgutil and visual functions - it is just an overlay
    inspect = imgutil.mix_rgb(red, green, blue)

    inspect *= 255
    if image.ndim == 2:
        image = skimage.color.gray2rgb(image)

    return imgutil.make_rgb(pred_alpha * inspect + (1 - pred_alpha) * image)


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
    return imgutil.make_rgb(pred_alpha * prediction_rgb + (1 - pred_alpha) * image)


def show_with_legend(images, legends, titles="", scale=None, legend_size=16):
    if not isinstance(images, list):
        images = [images]
    if not isinstance(legends, list):
        legends = [legends]
    elif not isinstance(legends[0], list):  # TODO it looks silly
        legends = [legends]
    if not isinstance(titles, list):
        titles = [titles]

    scale = scale or 30
    shape_ratio = images[0].shape[0] / images[0].shape[1]
    fig, axes = plt.subplots(1, len(images), figsize=(scale, scale * shape_ratio))
    if len(images) == 1:
        axes = [axes]

    for ax, image, legend, title in zip(axes, images, legends, titles):
        ax.set_aspect("auto")
        ax.set_title(title)
        legend_patches = [mpatches.Patch(color=colour, label=name) for name, colour in legend]
        ax.legend(handles=legend_patches, prop={'size': legend_size})
        ax.imshow(image)

    plt.close(fig)
    return fig
