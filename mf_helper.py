import os
import yaml
import subprocess
import re
from typing import List, Tuple, Union

from src.utils.utils import DashboardFinder


class MfHelper:
    def __init__(self):
        self.root_directory = "../"
        self.cache_directory = '.cache/'
        self.cache_directory_path = os.path.join(self.root_directory, self.cache_directory)

    def parse_dashboard_from_file(self, file_location: str) -> dict:
        with open(file_location, "r") as file:
            yaml_data = yaml.safe_load(file)
        # parses only the values associated with the "dashboards" key as it was stated in specification
        dashboards_spec = yaml_data.get("dashboards")

        return dashboards_spec

    def get_asset_info(self, dashboard_specs: dict):
        asset_info = []
        # loops through each dashboard if multiple is defined within the same yaml
        for idx, dashboard in enumerate(dashboard_specs):
            for num_of_ass, asset in enumerate(dashboard.get("assets")):
                asset_name = re.sub(r'[\s-]+', '_', asset.get("name").lower())  # changes str to snake-case
                metric_name = asset.get("metric")
                group_by = asset.get("group by")
                if asset_name and metric_name:
                    asset_info.append((asset_name, metric_name, group_by))
        return asset_info

    def create_cache_directory(self, package_name: Union[str, None] = None) -> Tuple[bool, str]:
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

    def download_cache_files(self, package_name: str, asset_name: str, metric_name: str, group_by: Union[str, None]) -> Tuple[bool, str]:
        cache_file_path = os.path.join(os.path.join(self.cache_directory_path, package_name), f"{asset_name}.csv")
        command = ["mf", "query", "--metrics", metric_name]

        if group_by is not None:
            command.extend(["--group-by", group_by])

        command.extend(["--csv", cache_file_path])

        try:
            print(f"command to be executed: {command}")
            result = subprocess.run(command, capture_output=True, check=True)
            print(result.stdout)
            return True, f"Downloaded {metric_name}.csv to {cache_file_path}"
        except subprocess.CalledProcessError as e:
            print(f"failed: {e}")
            return False, f"Error downloading {metric_name}.csv: {e}"

    def generate_multiple_cache_files(self, package_name: str, asset_info: List[tuple]):
        results = []
        for asset_name, metric_name, group_by in asset_info:
            success, message = self.download_cache_files(package_name, asset_name, metric_name, group_by)
            results.append((success, message))
        return results


if __name__ == '__main__':

    helper = MfHelper()
    helper.create_cache_directory()

    finder = DashboardFinder()
    dashboards_dir = finder.find_dashboards_dir()
    for filename in os.listdir(dashboards_dir):
        if filename.endswith(".yml"):
            file_path = os.path.join(dashboards_dir, filename)
            dashboard_data = helper.parse_dashboard_from_file(file_path)
            dashboard_package_name = dashboard_data[0].get("package_name")
            helper.create_cache_directory(dashboard_package_name)  # creates subdir in cache with given package_name
            info = helper.get_asset_info(dashboard_data)
            helper.generate_multiple_cache_files(dashboard_package_name, info)