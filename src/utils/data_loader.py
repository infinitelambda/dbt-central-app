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

        self.log_path = os.path.abspath(
            os.path.join(self.cache_directory_path, "data_loader.log")
        )

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
        cache_path = self.cache_directory_path

        if package_name is None:
            # Create log file & clear
            open(self.log_path, "w").close()

        if package_name:
            package_subdirectory = os.path.join(self.cache_directory_path, package_name)
            cache_path = package_subdirectory

        if not os.path.exists(cache_path):
            try:
                os.makedirs(cache_path)
                return True, f"Created {cache_path}"
            except OSError as e:
                return False, f"Error creating {cache_path}: {e}"
        else:
            return True, f"{cache_path} already exists."

    def download_cache_files(
        self,
        asset: AssetSerializer,
        package_name: str,
        dbt_path: str,
    ) -> Tuple[bool, str]:
        """
        Downloads applicable caches files

            Parameters:
                asset (AssetSerializer): Asset we're generating the mf command from
                package_name (str): Name of the package we are generating the asset for
                dbt_path (str): Path of the dbt project we wish to execute the command from
        """
        cache_file_path = os.path.abspath(
            os.path.join(
                os.path.join(self.cache_directory_path, package_name),
                f"{asset.asset_name}.csv",
            )
        )
        command = asset.generate_mf_query_command()

        command.extend(["--csv", cache_file_path])

        try:
            with open(self.log_path, "a") as file:
                file.write(f"Command to be executed: {' '.join(command)}\n")

            result = subprocess.run(command, capture_output=True, check=True, cwd=dbt_path)

            with open(self.log_path, "a") as file:
                file.write(f"Downloaded {asset.metric_name}.csv to {cache_file_path}\n")

            return True, f"Downloaded {asset.metric_name}.csv to {cache_file_path}"
        except subprocess.CalledProcessError as e:
            with open(self.log_path, "a") as file:
                file.write(f"Failed: {e}\n{e.stdout.decode()}\n")
            return False, f"Error downloading {asset.metric_name}.csv: {e}"

    def generate_multiple_cache_files(
        self, package_name: str, asset_info: List[AssetSerializer], dbt_path: str
    ):
        results = []

        for asset in asset_info:
            success, message = self.download_cache_files(
                asset=asset, package_name=package_name, dbt_path=dbt_path
            )
            results.append((success, message))
        return results

    def load(self, dbt_path: str):
        """
        Loads all relevant csv data

            Parameters:
                dbt_path (str): The path for the specific dbt project
                    from which the mf commands should be executed
        """
        self.create_cache_directory()

        finder = DashboardFinder()
        dashboards_dir = finder.find_dashboards_dir()

        for filename in os.listdir(dashboards_dir):
            if filename.endswith(".yml"):
                file_location = os.path.join(dashboards_dir, filename)
                dashboard_data = self.parse_dashboard_from_file(file_location=file_location)
                dashboard_package_name = dashboard_data[0].get("package_name")
                # creates subdir in cache with given package_name
                self.create_cache_directory(package_name=dashboard_package_name)
                info = self.get_asset_info(dashboard_spec=dashboard_data)
                self.generate_multiple_cache_files(
                    package_name=dashboard_package_name, asset_info=info, dbt_path=dbt_path
                )
