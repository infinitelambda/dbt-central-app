import os
import subprocess
from pathlib import Path
from typing import Tuple

import pandas as pd


class CacheMiss(Exception):
    pass


class Cache:
    def __init__(self):
        self.path = "../.cache"

    def fetch(self, package, metric) -> pd.DataFrame:
        try:
            return pd.read_csv(Path(self.path, package, metric + ".csv"))
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

    def download_cache_files(self, metric_name: str) -> Tuple[bool, str]:
        """
        Download cache files using 'mf query' and save them to the .cache directory.

        Note: Make sure 'mf' command-line tool is available and properly configured.

        Args:
             metric_name (str): The name of the metric to download.

        Returns:
            Tuple[bool, str]: A tuple containing a boolean indicating success (True if the download was
            successful, False otherwise), and a message string indicating the result or any errors.
        """
        # package_name = "dbt-tpch"; metric_name = "tpch_count_orders" # example values
        cache_file_path = os.path.join(self.cache_directory_path, f"{metric_name}.csv")

        try:
            subprocess.run([f"mf query --metrics {metric_name} --csv {cache_file_path}"],
                           capture_output=True, check=True, shell=True)
            return True, f"Downloaded {metric_name}.csv to {cache_file_path}"
        except subprocess.CalledProcessError as e:
            return False, f"Error downloading {metric_name}.csv: {e}"
