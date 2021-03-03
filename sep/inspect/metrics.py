from sep._commons import visuals


def overlay_visual_inspection(image, ground_truth, segmentation, pred_alpha=0.75):
    overlay = visuals.overlay_as_rgb(image, segmentation > ground_truth,
                                     (ground_truth == 1) & (segmentation == 1), ground_truth > segmentation,
                                     pred_alpha=pred_alpha)
    legend = [("True positive", (0, 1, 0)), ("False positive", (1, 0, 0)), ("False negative", (0, 0, 1))]
    return overlay, legend
