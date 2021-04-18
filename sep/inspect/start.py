import fire
import os
import pathlib
import shutil

inspect_dir_path = pathlib.Path(__file__).parent
inspect_dir_name = os.path.basename(inspect_dir_path)


def _jupyter(inspect_dir):
    command = f'cd {inspect_dir}'
    print("Starting jupyter inside:", command)
    os.system(command)
    os.chdir(inspect_dir)
    command = f'jupyter notebook'
    os.system(command)


def here():
    _jupyter(inspect_dir_path)


def from_copy(dir_to_copy_inspect_to):
    os.makedirs(dir_to_copy_inspect_to, exist_ok=True)
    shutil.copytree(pathlib.Path(__file__).parent, os.path.join(dir_to_copy_inspect_to, inspect_dir_name))
    _jupyter(dir_to_copy_inspect_to)


if __name__ == '__main__':
    fire.Fire()
