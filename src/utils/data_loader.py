import os
import yaml
import subprocess
import re
from typing import List, Tuple, Union

from utils.utils import DashboardFinder
from utils.serializers import AssetSerializer


class DataLoader:
    def __init__(self):
        self.root_directory = "../"
        self.cache_directory = ".cache/"
        self.cache_directory_path = os.path.join(self.root_directory, self.cache_directory)

    def parse_dashboard_from_file(
        self, file_location: str, dashboard_key: str = "dashboards"
    ) -> dict:
        """
        Extracts dashboard from specified valid .yml file

            Parameters:
                file_location (str): The location of the file to be parsed
                dashboard_key (str): Optional. Default - "dashboards"
                    can be passed to override default key for exporting dashboards data

            Returns:
                dashboard_spec (dict): Extracted dashboard
        """
        with open(file_location, "r") as file:
            yaml_data = yaml.safe_load(file)

        dashboards_spec = yaml_data.get(dashboard_key)

        return dashboards_spec

    def get_asset_info(self, dashboard_spec: dict) -> List[AssetSerializer]:
        """
        Provided a dashboard_spec dictionary - extracts all relevant assert information
        serializes them to Asset objects and returns the complete list

            Parameters:
                dashboard_spec (dict): Dashboard spec dictionary

            Returns:
                asset_info (List): All assets found in a specific dashboard
        """
        asset_info = []

        # loops through each dashboard if multiple is defined within the same yaml
        for idx, dashboard in enumerate(dashboard_spec):
            for num_of_ass, asset in enumerate(dashboard.get("assets")):
                serialized_asset = AssetSerializer(asset_dict=asset)

                # Break if asset is invalid or API asset
                if not serialized_asset.is_valid():
                    break

                asset_info.append(serialized_asset)

        return asset_info

    def create_cache_directory(
        self, package_name: Union[str, None] = None
    ) -> Tuple[bool, str]:
        """
        Creates or Gets a desired cached directory
        Will raise error upon failure
        """
        desired_path = self.cache_directory_path
        if package_name:
            package_subdirectory = os.path.join(self.cache_directory_path, package_name)
            desired_path = package_subdirectory

        if not os.path.exists(desired_path):
            try:
                os.makedirs(desired_path)
                return True, f"Created {desired_path}"
            except OSError as e:
                return False, f"Error creating {desired_path}: {e}"
        else:
            return True, f"{desired_path} already exists."

    def download_cache_files(
        self,
        asset: AssetSerializer,
        package_name: str,
    ) -> Tuple[bool, str]:
        """
        Downloads applicable caches files
        """
        cache_file_path = os.path.join(
            os.path.join(self.cache_directory_path, package_name),
            f"{asset.asset_name}.csv",
        )
        command = asset.generate_mf_query_command()

        try:
            print(f"command to be executed: {command}")
            result = subprocess.run(command, capture_output=True, check=True)
            print(result.stdout)
            return True, f"Downloaded {asset.metric_name}.csv to {cache_file_path}"
        except subprocess.CalledProcessError as e:
            print(f"failed: {e}")
            return False, f"Error downloading {asset.metric_name}.csv: {e}"

    def generate_multiple_cache_files(
        self, package_name: str, asset_info: List[AssetSerializer]
    ):
        results = []

        for asset in asset_info:
            success, message = self.download_cache_files(
                asset=asset, package_name=package_name
            )
            results.append((success, message))
        return results

    def load(self):
        self.create_cache_directory()

        finder = DashboardFinder()
        dashboards_dir = finder.find_dashboards_dir()

        for filename in os.listdir(dashboards_dir):
            if filename.endswith(".yml"):
                file_path = os.path.join(dashboards_dir, filename)
                dashboard_data = self.parse_dashboard_from_file(file_path)
                dashboard_package_name = dashboard_data[0].get("package_name")
                self.create_cache_directory(
                    dashboard_package_name
                )  # creates subdir in cache with given package_name
                info = self.get_asset_info(dashboard_data)
                results = self.generate_multiple_cache_files(dashboard_package_name, info)
