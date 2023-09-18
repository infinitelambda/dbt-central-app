import os
import yaml
import subprocess
from typing import List, Tuple


class DashboardFinder:
    """
    A class for finding the 'dashboards' directory recursively.
    """

    def __init__(self, start_path: str = None):
        """
        Initialize the DashboardFinder.

        :param start_path: The starting directory path (default is the current working directory).
        :type start_path: str
        """
        self.start_path = start_path or os.getcwd()

    def _validate_directory(self, directory: str) -> str:

        # Check if the 'dashboards' directory exists in the specified directory.
        dashboards_dir = os.path.join(directory, 'dashboards')
        return dashboards_dir if os.path.exists(dashboards_dir) and os.path.isdir(dashboards_dir) else None

    def find_dashboards_dir(self) -> str:
        """
        Find the 'dashboards' directory recursively starting from the specified path.

        :return: The path to the 'dashboards' directory if found, otherwise a message indicating it was not found.
        :rtype: str
        """
        current_directory = self.start_path

        for root, _, _ in os.walk(current_directory):
            dashboards_path = self._validate_directory(root)
            if dashboards_path:
                return dashboards_path

        # TODO implement similar solution like in `create_cache_directory():`
        return "The 'dashboards' directory was not found in the specified path, parent directory, or any of its child directories."


class YamlParser:
    """
    A class for parsing YAML files containing dashboard data.

    Args:
        dashboards_dir (str): The directory path containing YAML files to parse.
    """

    def __init__(self, dashboards_dir: str):
        self.dashboards_dir = dashboards_dir

    def _parse_dashboard_from_file(self, file_path: str) -> List[dict]:

        with open(file_path, "r") as file:
            yaml_data = yaml.safe_load(file)

        # Assuming after the "version" comes the 'dashboard description' without requiring any naming convention
        stripped_dashboard_data = list(yaml_data.values())[1]
        return stripped_dashboard_data

    def _parse_yaml_files(self) -> List[dict]:

        parsed_data = []
        for filename in os.listdir(self.dashboards_dir):
            if filename.endswith(".yml"):
                file_path = os.path.join(self.dashboards_dir, filename)
                dashboard_data = self._parse_dashboard_from_file(file_path)
                parsed_data.extend(dashboard_data)
        return parsed_data

    def get_raw_data(self) -> List[dict]:
        """
        Get the raw dashboard data parsed from YAML files.

        Returns:
            list: A list of dictionaries, each containing dashboard information.
        """
        return self._parse_yaml_files()


class CacheDirectoryManager:
    """A class for managing the .cache directory."""

    def __init__(self, root_directory: str = './'):
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

    def download_cache_files(self, package_name: str, metric_name: str) -> Tuple[bool, str]:
        """
        Download cache files using 'mf query' and save them to the .cache directory.

        Note: Make sure 'mf' command-line tool is available and properly configured.

        Args:
             package_name (str): The name of the package to download cache files from.
             metric_name (str): The name of the metric to download.

        Returns:
            Tuple[bool, str]: A tuple containing a boolean indicating success (True if the download was
            successful, False otherwise), and a message string indicating the result or any errors.
        """
        # package_name = "dbt-tpch"; metric_name = "tpch_count_orders" # example values
        cache_file_path = os.path.join(self.cache_directory_path, f"{package_name}/{metric_name}.csv")

        try:
            subprocess.run(["mf", "query",
                            "--metrics", f"{metric_name}",
                            "--group-by", "metric_time__month",
                            "--csv", cache_file_path],
                           capture_output=True, check=True, shell=True)
            return True, f"Downloaded {metric_name}.csv to {cache_file_path}"
        except subprocess.CalledProcessError as e:
            return False, f"Error downloading {metric_name}.csv: {e}"
