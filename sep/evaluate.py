import os
import typing
from pathlib import Path

import pandas as pd
from tqdm import tqdm

from sep.assessors.detailer import Detailer
from sep.assessors.metricer import Metricer
from sep.loaders import Loader
from sep.producers import Producer


def evaluate(data_loader: Loader, producer: Producer, metricer: Metricer,
             detailer: typing.Optional[Detailer], output_evalpath=None,
             verbose=1):
    if verbose:
        print(f"Evaluation of {producer} on data from {data_loader}.")
        print(f"There are {len(data_loader)} images to evaluate on.", flush=True)

    if output_evalpath is not None:
        os.makedirs(output_evalpath, exist_ok=True)

    for i in tqdm(range(len(data_loader)), producer.name):
        image = data_loader.load_image(i)
        gt = data_loader.load_annotation(i)
        tag = data_loader.load_tag(i)

        if gt is None:
            print(data_loader.list_images()[i], "does not have annotation data!")

        segment, segment_tag = producer.calculate(image, tag)
        data_point_eval = metricer.evaluate_image(image, tag, segment, segment_tag, gt)
        if detailer is not None:  # TODO detailer vs metricer relation has to be rethought
            detailer.save_image_evaluation(data_point_eval)

    return metricer.report_overall()


def compare(data_loader: Loader, producers: typing.List[Producer], metricer, detailer, output_evalpath):
    print(f"Comparison of {len(producers)} producers on data from {data_loader}.", flush=True)

    reports = []
    for producer in producers:
        if output_evalpath is not None:
            producer_eval_path = Path(output_evalpath) / producer.name
        else:
            producer_eval_path = None
        producer_report = evaluate(data_loader, producer, metricer, detailer, producer_eval_path,
                                   verbose=0)
        producer_report.insert(loc=0, column='producer', value=producer.name)

        reports.append(producer_report)
    return pd.concat(reports).groupby(['producer', 'region']).mean()
