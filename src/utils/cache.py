import os
from pathlib import Path
from typing import Tuple

import pandas as pd


class CacheMiss(Exception):
    pass


class Cache:
    def __init__(self):
        self.path = "../.cache"

    def fetch(self, package, asset_name) -> pd.DataFrame:
        try:
            return pd.read_csv(Path(self.path, package, asset_name + ".csv"))
        except FileNotFoundError:
            raise CacheMiss()


class CacheDirectoryManager:
    """A class for managing the .cache directory."""

    def __init__(self, root_directory: str = '../'):
        """
        Initialize the CacheDirectoryManager.

        Args:
            root_directory (str): The root directory where the .cache directory will be managed.
        """
        self.root_directory = root_directory
        self.cache_directory = '.cache'
        self.cache_directory_path = os.path.join(self.root_directory, self.cache_directory)

    def create_cache_directory(self) -> Tuple[bool, str]:
        """
        Create the .cache directory if it doesn't exist.

        Returns:
            bool: True if the directory was created or already exists, False if there was an error.
            str: A message indicating the result.
        """
        if not os.path.exists(self.cache_directory_path):
            try:
                os.makedirs(self.cache_directory_path)
                return True, f"Created {self.cache_directory_path}"
            except OSError as e:
                return False, f"Error creating {self.cache_directory_path}: {e}"
        else:
            return True, f"{self.cache_directory_path} already exists."


if __name__ == '__main__':
    CacheDirectoryManager().create_cache_directory()
