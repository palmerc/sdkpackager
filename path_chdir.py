import os
from pathlib import Path


class Chdir(object):
    def __init__(self, path):
        self.path = Path(path)

    def __enter__(self):
        self.saved_path = Path.cwd()
        os.chdir(self.path)

    def __exit__(self, *args):
        os.chdir(self.saved_path)