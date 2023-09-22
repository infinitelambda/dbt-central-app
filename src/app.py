import abc
from pathlib import Path
from src.utils.utils import YamlParser, DashboardFinder

import pandas as pd
import streamlit


class CacheMiss(Exception):
    pass


class Cache:
    def __init__(self):
        self.path = "../.cache"

    def fetch(self, package, metric):
        try:
            return pd.read_csv(Path(self.path, package, metric + ".csv"))
        except FileNotFoundError:
            raise CacheMiss()


class Asset(abc.ABC):
    def __init__(self, cache, dashboard, spec):
        self.cache = cache
        self.dashboard = dashboard
        self.spec = spec

    def fetch_metric_data(self):
        return self.cache.fetch(package=self.dashboard.get("package_name"), metric=self.spec.get("metric"))

    def sort_metric_data(self, data):
        data = self.fetch_metric_data()
        return data.sort_values(by=[self.spec.get("sort_by")], ascending=self.spec.get("ascending"))

    def display(self):
        try:
            data = self.fetch_metric_data()
            data = self.sort_metric_data(data)
            self.chart(data)
        except CacheMiss:
            streamlit.warning(f"Could not find data for metric `{self.spec.get('metric')}`.", icon="⚠️")

    @abc.abstractmethod
    def chart(self, data):
        pass


class LineChartAsset(Asset):

    def chart(self, data):
        streamlit.line_chart(data, x=self.spec.get("x"), y=self.spec.get("y"))


class TableAsset(Asset):

    def chart(self, data):
        streamlit.dataframe(data)


class AssetStreamlitChartMap:
    chart = {
        "line_chart": LineChartAsset,
        "table": TableAsset
    }


class App:
    def __init__(self):
        self.ctx = self._load_context()
        self.cache = self._load_cache()

    def _load_context(self):
        finder = DashboardFinder()
        dashboards_path = finder.find_dashboards_dir()
        parser = YamlParser(dashboards_path)
        context = parser.get_raw_data()
        return context

    def _load_cache(self):
        # TODO: Decide on caching approach
        return Cache()

    def run(self):
        # Generate dashboard objects
        pages = dict()
        for idx, dashboard_spec in enumerate(self.ctx):
            package_name = dashboard_spec.get("package_name")
            assets = list()
            pages[package_name] = (idx, assets)
            for asset_spec in dashboard_spec.get("assets"):
                asset = AssetStreamlitChartMap.chart.get(asset_spec.get("type"))
                assets.append(asset(self.cache, dashboard_spec, asset_spec))

        # Display sidebar
        packages = [dashboard.get("package_name") for dashboard in self.ctx]
        with streamlit.sidebar:
            streamlit.title("dbt Dashboards")
            streamlit.subheader("A central place for all your dbt related metrics.")
            option = streamlit.selectbox("Select a dbt package from the list below.", packages)

        # Display selected dashboard
        dashboard_idx, assets = pages.get(option)
        dashboard_spec = self.ctx[dashboard_idx]

        streamlit.title(dashboard_spec.get("name"))
        streamlit.text(dashboard_spec.get("description"))
        for asset in assets:
            streamlit.header(asset.spec.get("title"))
            streamlit.text(asset.spec.get("description"))
            asset.display()
            streamlit.divider()


if __name__ == '__main__':
    App().run()
