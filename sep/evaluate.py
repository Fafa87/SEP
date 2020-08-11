import os
import typing
from pathlib import Path

import pandas as pd
from tqdm import tqdm

from sep.loaders.loader import Loader
from sep.producers.producer import Producer


def evaluate(data_loader: Loader, producer: Producer, metricer, detailer, output_evalpath):
    print(f"Evaluation of {producer} on data from {data_loader}.")
    print(f"There are {len(data_loader)} images to evaluate on.")
    os.makedirs(output_evalpath, exist_ok=True)

    for i in range(tqdm(len(data_loader), "Evaluating")):
        image = data_loader.load_image(i)
        gt = data_loader.load_annotation(i)
        tag = data_loader.load_tag(i)

        if gt is None:
            print(data_loader.list_images()[i], "does not have annotation data!")

        segment, segment_tag = producer.calculate(image, tag)
        data_point_eval = metricer.evaluate_image(image, tag, segment, segment_tag, gt)
        detailer.save_image_evaluation(data_point_eval)

    return metricer.report_overall()


def compare(data_loader: Loader, producers: typing.List[Producer], metricer, detailer, output_evalpath):
    print(f"Comparison of {len(producers)} producers on data from {data_loader}.")

    reports = pd.DataFrame()
    for producer in producers:
        producer_eval_path = Path(output_evalpath) / producer.name
        producer_report = evaluate(data_loader, producer, metricer, detailer, producer_eval_path)
        producer_report.insert(loc=0, column='Producer', value=producer.name)

        reports = reports.concat(producer_report)
    return reports
