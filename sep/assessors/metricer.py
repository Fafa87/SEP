import typing

import numpy as np
import pandas as pd

from sep.assessors.metrics import Metric
from sep.assessors.regions import Region, EntireRegion


class Metricer:
    """
    This is class responsible for generating a set of metrics for various image regions.
    """
    metrics: typing.List[Metric]
    regions: typing.List[Region]

    def __init__(self):
        self.metrics = []
        self.regions = [EntireRegion()]

    def calculate_metrics(self, segmentation, ground_truth):
        reports = []
        for region in self.regions:
            seg_region = region.regionize(ground_truth=ground_truth, mask=segmentation)
            gt_region = region.regionize(ground_truth=ground_truth, mask=ground_truth)

            metrics_region = {metric.name: metric.calculate(seg_region, gt_region) for metric in self.metrics}
            region_report = pd.DataFrame.from_records([metrics_region])
            region_report["region"] = region.name
            reports.append(region_report)
        return pd.concat(reports)

    def report_overall(self):
        """
        This should aggregate all the collected results.

        result_sample per image:
            id, name, *img_tag, *seg_tag, metrics (region_A_iou, region_A_path?, region_B_iou ..., iou_avg)

        result_sample per grouping:
            group_name, *seg_tag_avg, general_path_to_details??, region_A_iou_avg, region_B_iou_avg , iou_avg

        result_sample per entire run (single line):
            segmentator_name, *seg_tag_avg, region_A_iou_avg, region_B_iou_avg, iou_avg

        Returns:

        """
        pass

    def evaluate_image(self, image: np.ndarray, tag: dict, segment: np.ndarray, segment_tag: dict,
                       gt: np.ndarray) -> pd.DataFrame:

        """
        Evaluate the given image, ground truth and segmentation and store and aggregate the metrics report.
        """

        pass
