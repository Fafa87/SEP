from abc import ABC, abstractmethod

import pandas as pd
import typing

from sep.assessors.metrics import Metric
from sep.assessors.regions import Region


class Metricer:
    """
    This is class responsible for generating a set of metrics for various image regions.
    """
    metrics: typing.List[Metric]
    regions: typing.List[Region]

    def __init__(self):
        self.metrics = []
        self.regions = [Region()]

    def calculate_metrics(self, segmentation, ground_truth):
        reports = []
        for region in self.regions:
            seg_region = region.regionize(ground_truth=ground_truth, mask=segmentation)
            gt_region = region.regionize(ground_truth=ground_truth, mask=ground_truth)

            metrics_region = {metric.name: metric.calculate(seg_region, gt_region) for metric in self.metrics}
            region_report = pd.DataFrame.from_records([metrics_region])
            reports.append(region_report)
        return pd.concat(reports)
