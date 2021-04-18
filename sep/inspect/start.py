import fire
import os
import pathlib
import shutil


def _jupyter(inspect_dir):
    command = f'cd {inspect_dir}'
    print("Starting jupyter inside:", command)
    os.system(command)
    os.chdir(inspect_dir)
    command = f'jupyter notebook'
    os.system(command)


def here():
    inspect_dir = str(pathlib.Path(__file__).parent)
    _jupyter(inspect_dir)


def from_copy(path_to_copy_inspect_to):
    shutil.copytree(pathlib.Path(__file__).parent, path_to_copy_inspect_to)
    _jupyter(path_to_copy_inspect_to)


if __name__ == '__main__':
    fire.Fire()
