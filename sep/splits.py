import os

import collections
import fire
from pathlib import Path

from sep.loaders import FilesLoader


def validate(*split_listings: str, use_file_path=False):
    data_splits = {}
    for listing_path in split_listings:
        listing_name = Path(listing_path).name
        print(f"Listing: {listing_name}...")
        loader = FilesLoader.from_listing("", filepath=listing_path, validate_list=False)
        print(f"... consist of {len(loader)} samples.")
        data_splits[listing_name] = loader

    # Validate duplicates:
    for split in data_splits:
        if use_file_path:
            split_files = data_splits[split].list_images_paths()
        else:
            split_files = [os.path.basename(img) for img in data_splits[split].list_images()]  # TODO ensure that those are names

        duplicated_files = [item for item, count in collections.Counter(split_files).items() if count > 1]
        if duplicated_files:
            print(f"There are duplications in listing {split}:")
            print(f"There are {len(duplicated_files)} duplicates, for example:")
            print(", ".join(list(duplicated_files)[:10]))

    # Validate separation:
    for split1 in data_splits:
        for split2 in data_splits:
            if split1 < split2:  # ensure only once
                if use_file_path:
                    split1_files = data_splits[split1].list_images_paths()
                    split2_files = data_splits[split2].list_images_paths()
                else:
                    split1_files = data_splits[split1].list_images()
                    split2_files = data_splits[split2].list_images()

                overlap = set(split1_files) & set(split2_files)
                if overlap:
                    print(f"There is overlap between listings {split1} and {split2}:")
                    print(f"{len(overlap)} files are overlaping, for example:")
                    print(", ".join(list(overlap)[:10]))


if __name__ == '__main__':
    fire.Fire()
