import fire
import napari

import sep.loaders
from sep._commons.gui import Inspector, add_review_option, ReviewEnum


def inspect_loader(data_loader):
    with napari.gui_qt():
        inspector = Inspector(data_loader)
        inspector.create_viewer()
        # TODO show and edit tags?
        # TODO show statistics?


def filter_loader_manual(data_loader: sep.loaders.FilesLoader, save_tags=False):
    """
    Start dataset filtering procedure using napari gui of the provided data_loader.
    Mark the unwanted samples as rejected. The data_loader will be reduce not to include those.
    Args:
        data_loader: original data_loader that will be filtered
    """
    print(f"Inspected loaded has {len(data_loader)} samples.")
    inspector = Inspector(data_loader)
    with napari.gui_qt():
        inspector.create_viewer()
        add_review_option(inspector)
    new_tags = inspector.viewer_state['temporary_tags']

    # TODO handle some sort of cancel?
    assert not save_tags, "Not yet implemented"

    all_samples = enumerate(data_loader.list_images())
    rejected_samples = []
    non_rejected_samples = []
    for num, name in all_samples:
        if num in new_tags and new_tags[num].get('review', ReviewEnum.No) == ReviewEnum.Rejected:
            rejected_samples.append(name)
        else:
            non_rejected_samples.append(name)

    print(f"Manual inspection rejected {len(rejected_samples)} samples.")
    if len(rejected_samples):
        print(f"List: {', '.join(rejected_samples)}")
    data_loader.filter_files(non_rejected_samples)
    assert len(data_loader) == len(non_rejected_samples)
    print(f"Now loader has {len(data_loader)} samples.")


def filter_dataset_listing(data_root, listing_path, output_path, verbose=1,
                           add_tag_path=True, ensure_samples_exist=True, preserve_order=True):
    if verbose:
        print(f"Filtering listing file {listing_path}.")
        print(f"The data root for dataset is {data_root}.")
        print(f"The new filtered listing (without rejected samples) will be saved to {output_path}.")

    loader = sep.loaders.ImagesLoader.from_listing(data_root, listing_path,
                                                   verbose=1, validate_list=ensure_samples_exist, preserve_order=preserve_order)
    filter_loader_manual(loader)
    loader.save(output_path, add_tag_path)


if __name__ == '__main__':
    fire.Fire()
