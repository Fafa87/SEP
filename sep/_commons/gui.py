from copy import deepcopy
from enum import Enum

import napari
import numpy as np
from magicgui import magicgui

from sep._commons.imgutil import get_2d_size


class Inspector:
    # Base class which wraps the common extension paths yet still allow to use full power of napari.
    # TODO docs
    # TODO add standard tags usage
    # TODO add information about the name of the current file
    def __init__(self, samples_collection, additional_tags: dict = None):
        self.samples_collection = samples_collection
        self.collection_size = len(samples_collection)
        self.viewer_state = {"current": 0, 'current_tag': {}, 'temporary_tags': {}}
        self.current_tags_state = self.viewer_state['temporary_tags']
        self.additional_tags = additional_tags or dict()
        self.load_tag_to_control = None
        self.viewer = None

    def set_load_tag_to_control(self, load_tag_to_control):
        self.load_tag_to_control = load_tag_to_control

    def get_or_copy_tags(self, sample_num):
        if sample_num not in self.current_tags_state:
            self.current_tags_state[sample_num] = deepcopy(self.samples_collection[sample_num]['tag'])
            if self.additional_tags is not None:  # add new tags only for inspection?
                self.current_tags_state[sample_num].update(self.additional_tags)
        return self.current_tags_state[sample_num]

    def get_labels_or_empty(self, sample_num):
        annotation = self.samples_collection[sample_num]['annotation']
        if annotation is None:  # fill in with dummy
            image = self.samples_collection[sample_num]['image']
            annotation = np.zeros(get_2d_size(image), dtype=np.uint8)
        return annotation

    @property
    def viewer_created(self):
        return self.viewer is not None

    def create_viewer(self):
        self.viewer = napari.Viewer()
        self.input_image = self.viewer.add_image(self.samples_collection[0]['image'], rgb=True)
        self.label_image = self.viewer.add_labels(self.get_labels_or_empty(0))

        @magicgui(
            auto_call=True,
            Sample={"widget_type": "IntSlider", "max": self.collection_size - 1},
        )
        def change_sample(Sample: int):
            self.set_sample(Sample)

        self.set_sample(0)
        self.viewer.window.add_dock_widget(change_sample)

        @self.viewer.bind_key('z')
        def prev_label(event=None):
            change_sample.Sample.value = (self.viewer_state["current"] - 1 + self.collection_size) % self.collection_size

        @self.viewer.bind_key('c')
        def next_label(event=None):
            change_sample.Sample.value = (self.viewer_state["current"] + 1 + self.collection_size) % self.collection_size

    def set_sample(self, new_cur):
        current = (new_cur + self.collection_size) % self.collection_size
        self.viewer_state["current"] = current

        self.input_image.data = self.samples_collection[current]['image']
        self.label_image.data = self.get_labels_or_empty(current)

        self.viewer_state['current_tag'] = self.get_or_copy_tags(current)
        if self.load_tag_to_control:
            self.load_tag_to_control(self.viewer_state['current_tag'])


class ReviewEnum(Enum):
    No = 0
    Approved = 1
    Rejected = 2


def add_review_option(inspector):
    inspector.additional_tags['review'] = ReviewEnum.No

    # Extend inspector with the additional tag representing the sample review state.
    def load_tags(current_tag):
        tags_properties.Review.value = inspector.viewer_state['current_tag'].get('review', ReviewEnum.No)

    @magicgui(auto_call=True)
    def tags_properties(Review: ReviewEnum):
        inspector.viewer_state['current_tag']['review'] = Review

    inspector.set_load_tag_to_control(load_tags)
    assert inspector.viewer_created, "Viewer has to be crated for binding new keys."

    @inspector.viewer.bind_key('1')
    def approve_move_key(event=None):
        tags_properties.Review.value = ReviewEnum.Approved
        inspector.viewer.keymap['C']()  # move to the next

    @inspector.viewer.bind_key('2')
    def reject_move_key(event=None):
        tags_properties.Review.value = ReviewEnum.Rejected
        inspector.viewer.keymap['C']()  # move to the next

    @inspector.viewer.bind_key('`')
    def back_move_key(event=None):
        inspector.viewer.keymap['Z']()  # move to the next

    inspector.viewer.window.add_dock_widget(tags_properties)

    return inspector
