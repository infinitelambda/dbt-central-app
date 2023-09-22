import os
import yaml
import subprocess
from typing import List, Tuple, Union


class MfHelper:
    def __init__(self, ):
        self.file_path = "./adrien/dashboard/dbt_project_evaluator.yml"
        self.dashboard_specs = self._parse_dashboard_from_file()
        self.root_directory = "./adrien/"
        self.cache_directory = '.cache'
        self.cache_directory_path = os.path.join(self.root_directory, self.cache_directory)

    def _parse_dashboard_from_file(self) -> dict:
        with open(self.file_path, "r") as file:
            yaml_data = yaml.safe_load(file)

        dashboards_spec = yaml_data.get("dashboards")

        return dashboards_spec

    def get_metric_names(self):
        metric_names = []
        for idx, dashboard in enumerate(self.dashboard_specs):
            for asset in dashboard.get("assets"):
                metric_name = asset.get("metric")
                if metric_name:
                    metric_names.append(metric_name)
        return metric_names

    def create_cache_directory(self) -> Tuple[bool, str]:

        if not os.path.exists(self.cache_directory_path):
            try:
                os.makedirs(self.cache_directory_path)
                return True, f"Created {self.cache_directory_path}"
            except OSError as e:
                return False, f"Error creating {self.cache_directory_path}: {e}"
        else:
            return True, f"{self.cache_directory_path} already exists."

    def download_cache_files(self, metric_name: str) -> Tuple[bool, str]:
        cache_file_path = os.path.join(self.cache_directory_path, f"{metric_name}.csv")

        try:
            subprocess.run(["mf", "query",
                            "--metrics", f"{metric_name}",
                            "--csv", cache_file_path],
                           capture_output=True, check=True, shell=True)
            return True, f"Downloaded {metric_name}.csv to {cache_file_path}"
        except subprocess.CalledProcessError as e:
            return False, f"Error downloading {metric_name}.csv: {e}"

    def generate_multiple_cache_files(self, metric_names: List[str]):
        results = []
        for metric_name in metric_names:
            success, message = self.download_cache_files(metric_name)
            results.append((success, message))
        return results


if __name__ == '__main__':
    helper = MfHelper()
    metrics = helper.get_metric_names()
    helper.create_cache_directory()
    helper.generate_multiple_cache_files(metrics)
