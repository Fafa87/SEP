import pathlib

import os

if __name__ == '__main__':
    inspect_dir = str(pathlib.Path(__file__).parent)
    command = f'cd {inspect_dir}'
    print("Starting jupyter inside:", command)
    os.system(command)
    os.chdir(inspect_dir)
    command = f'jupyter notebook'
    os.system(command)
