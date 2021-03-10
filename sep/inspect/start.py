import pathlib

import os

# TODO option to copy the notebook to new folder (e.g. where the project is happening)

if __name__ == '__main__':
    inspect_dir = str(pathlib.Path(__file__).parent)
    command = f'cd {inspect_dir}'
    print("Starting jupyter inside:", command)
    os.system(command)
    os.chdir(inspect_dir)
    command = f'jupyter notebook'
    os.system(command)
