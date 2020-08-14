import unittest

import sep.assessors.metricer
import sep.assessors.metrics
import sep.evaluate
import sep.loaders.images
import sep.producers.producer
import tests.testbase


class TestEvaluate(tests.testbase.TestBase):
    class Threshold(sep.producers.producer.Producer):
        def __init__(self, channel, cache_root):
            super().__init__(name=f"Threshold_on_{channel}", cache_root=cache_root)
            self.channel = channel

        def segmentation(self, image):
            return image[..., self.channel] > 0.5

    def test_evaluate_simple(self):
        test_images_loader = sep.loaders.images.ImagesLoader("input")
        output_dir = self.create_temp_dir()

        producer_red = self.Threshold(0, self.create_temp_dir())
        metricer = sep.assessors.metricer.Metricer()
        metricer.metrics.append(sep.assessors.metrics.IouMetric())

        report = sep.evaluate.evaluate(data_loader=test_images_loader, producer=producer_red,
                                       metricer=metricer, detailer=None, output_evalpath=output_dir)
        self.assertEqual(2, len(report))


if __name__ == '__main__':
    unittest.main()
