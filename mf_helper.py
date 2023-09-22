import os
import yaml
import subprocess
import re
from typing import List, Tuple, Union


class MfHelper:
    def __init__(self, dashboard_file_path):
        self.dashboard_file_path = dashboard_file_path
        self.dashboard_specs = self._parse_dashboard_from_file()
        self.root_directory = "../adrien/"
        self.cache_directory = '.cache/'
        self.cache_directory_path = os.path.join(self.root_directory, self.cache_directory)

    def _parse_dashboard_from_file(self) -> dict:
        with open(self.dashboard_file_path, "r") as file:
            yaml_data = yaml.safe_load(file)
        # parses only the values associated with the "dashboards" key as it was stated in specification
        dashboards_spec = yaml_data.get("dashboards")

        return dashboards_spec

    def get_asset_info(self):
        asset_info = []
        # loops through each dashboard if multiple is defined within the same yaml
        for idx, dashboard in enumerate(self.dashboard_specs):
            for num_of_ass, asset in enumerate(dashboard.get("assets")):
                asset_name = re.sub(r'[\s-]+', '_', asset.get("name").lower())  # changes str to snake-case
                metric_name = asset.get("metric")
                group_by = asset.get("group by")
                if asset_name and metric_name:
                    asset_info.append((asset_name, metric_name, group_by))
            # temporary for testing. All 3 sample yaml contains asset with and without a group_by in the first 2 place
                if num_of_ass == 1:
                    break
        return asset_info

    def create_cache_directory(self) -> Tuple[bool, str]:

        if not os.path.exists(self.cache_directory_path):
            try:
                os.makedirs(self.cache_directory_path)
                return True, f"Created {self.cache_directory_path}"
            except OSError as e:
                return False, f"Error creating {self.cache_directory_path}: {e}"
        else:
            return True, f"{self.cache_directory_path} already exists."

    def download_cache_files(self, asset_name: str, metric_name: str, group_by: Union[str, None]) -> Tuple[bool, str]:
        cache_file_path = os.path.join(self.cache_directory_path, f"{asset_name}.csv")
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

    def generate_multiple_cache_files(self, asset_info: List[tuple]):
        results = []
        for asset_name, metric_name, group_by in asset_info:
            success, message = self.download_cache_files(asset_name, metric_name, group_by)
            results.append((success, message))
        return results


if __name__ == '__main__':
    dashboard_path_to_load = "../adrien/dashboard/dbt_project_evaluator.yml"
    helper = MfHelper(dashboard_path_to_load)
    info = helper.get_asset_info()
    helper.create_cache_directory()
    # short_cmd = helper.download_cache_files(asset_name="test-for-short-dbt-cloud-snowflake-demo-main",
    #                                         metric_name="dbt_project_evaluator_root_models",
    #                                         group_by=None)
    #
    # long_cmd = helper.download_cache_files(asset_name="test-for-long-dbt-cloud-snowflake-demo-main",
    #                                        metric_name="dbt_project_evaluator_root_models",
    #                                        group_by="fct_root_models__child,fct_root_models__current_date,metric_time")
    # tested until this point
    helper.generate_multiple_cache_files(info)
