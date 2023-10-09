import os
import yaml
from typing import List, Union


class InvalidYamlSpecification(BaseException):
    pass


class DashboardFinder:
    """
    A class for finding the 'dashboards' directory recursively.
    """

    def __init__(self, start_path: str = "../"):
        """
        Initialize the DashboardFinder.

        :param start_path: The starting directory path (default is the current working directory).
        :type start_path: str
        """
        self.start_path = start_path

    def find_dashboards_dir(self) -> str:
        """
        Find the 'dashboards' directory recursively starting from the specified path.

        :return: The path to the first 'dashboards' directory if found, otherwise a message indicating it was not found.
        :rtype: str
        """
        current_directory = self.start_path

        for root, subdirectories, filenames in os.walk(current_directory):
            valid_path = self._validate_directory(root)
            if valid_path:
                return valid_path

    def _validate_directory(self, directory: str) -> Union[str, None]:

        # Check if the 'dashboards' directory exists in the specified directory.
        # TODO ??exclude .venv hardcoded to reduce lookup time?
        try:
            dashboards_dir = os.path.join(directory, 'dashboards')
            if os.path.exists(dashboards_dir) and os.path.isdir(dashboards_dir):
                return dashboards_dir
        except (OSError, PermissionError) as e:
            print(f"Error while checking directory '{directory}': {e}")
            return None


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

        dashboards_spec = yaml_data.get("dashboards")
        return dashboards_spec

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


class ValidateUserYaml:
    EXPECTED_DASHBOARD_ATTRIBUTES = ["name", "title", "package_name", "assets"]
    EXPECTED_ASSET_ATTRIBUTES = ["name", "title", "metric", "type"]

    def validate_dashboard(self, parsed_dashboard: dict):
        if not all(attr in parsed_dashboard for attr in self.EXPECTED_DASHBOARD_ATTRIBUTES):
            raise InvalidYamlSpecification(self.EXPECTED_DASHBOARD_ATTRIBUTES)

    def validate_asset(self, parsed_asset: dict):

        if not all(attr in parsed_asset for attr in self.EXPECTED_ASSET_ATTRIBUTES):
            raise InvalidYamlSpecification(f"{self.EXPECTED_ASSET_ATTRIBUTES} utils")
