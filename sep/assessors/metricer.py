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
        self.reports = []

    def reset(self):
        self.reports = []

    def calculate_metrics(self, segmentation: np.ndarray, ground_truth: np.ndarray) -> pd.DataFrame:
        reports = []
        proper_report_columns_order = [metric.name for metric in self.metrics]
        proper_report_columns_order.insert(0, "region")

        for region in self.regions:
            seg_region = region.regionize(ground_truth=ground_truth, mask=segmentation)
            gt_region = region.regionize(ground_truth=ground_truth, mask=ground_truth)

            metrics_region = {metric.name: metric.calculate(seg_region, gt_region) for metric in self.metrics}
            region_report = pd.DataFrame.from_records([metrics_region])
            region_report["region"] = region.name
            reports.append(region_report)
        return pd.concat(reports).reindex(proper_report_columns_order, axis=1)

    def report_overall(self):
        """
        This should aggregate all the collected results.
        result_sampler per image region
            id, *img_tag, *seg_tag, iou, recall..., region_eval_path

        result_sample per image:
            id, name, *img_tag, *seg_tag, metrics (region_A_iou, region_A_path?, region_B_iou ..., iou_avg)

        result_sample per grouping:
            group_name, *seg_tag_avg, general_path_to_details??, region_A_iou_avg, region_B_iou_avg , iou_avg

        result_sample per entire run (single line):
            segmentator_name, *seg_tag_avg, region_A_iou_avg, region_B_iou_avg, iou_avg

        Returns:

        """
        # TODO multiple levels of aggregation
        return pd.concat(self.reports).fillna('').groupby(['region']).mean()

    def report_full(self):
        return pd.concat(self.reports).fillna('').reset_index(drop=True)

    def evaluate_image(self, image: np.ndarray, tag: dict, segment: np.ndarray, segment_tag: dict,
                       gt: np.ndarray) -> pd.DataFrame:

        """
        Evaluate the given image, ground truth and segmentation and store and aggregate the metrics report.
        """
        metric_report = self.calculate_metrics(segmentation=segment, ground_truth=gt)
        metric_report.insert(0, "id", tag["id"])
        # TODO multilayer tagging
        for (k, v) in tag.items():
            if k != "id":
                metric_report["img_" + k] = v

        for (k, v) in segment_tag.items():
            metric_report["seg_" + k] = v

        self.reports.append(metric_report)
        return metric_report
