from pathlib import Path

import yaml
import pandas as pd
import streamlit


context = yaml.safe_load("""
version: 2
dashboards:
  - name: TPCH Dashboards
    title: Dashboards for the TCPH project
    description: Dashboards for the TCPH project 
    package_name: dbt-tpch
    assets:
      - name: Orders
        title: TCPH Orders
        description: Order count by month.
        metric: tpch_count_orders
        type: line_chart
        sort_by: TPCH_COUNT_ORDERS
        ascending: False
        x: METRIC_TIME__MONTH
        y: TPCH_COUNT_ORDERS
      
      - name: Orders Details
        title: TCPH Orders Details
        description: Order count detailed.
        metric: tpch_count_orders
        type: table
        sort_by: METRIC_TIME__MONTH
        ascending: True
""")


class Cache:
    def __init__(self):
        self.path = ".cache"

    def fetch(self, package, metric):
        return pd.read_csv(Path(self.path, package, metric + ".csv"))


class Asset:
    def __init__(self, cache, dashboard, spec):
        self.cache = cache
        self.dashboard = dashboard
        self.spec = spec

    def fetch_metric_data(self):
        # TODO: check we can have only one metric per asset
        # TODO: define logic if multiple metrics
        return self.cache.fetch(package=self.dashboard.get("package_name"), metric=self.spec.get("metric"))

    def sort_metric_data(self, data):
        data = self.fetch_metric_data()
        return data.sort_values(by=[self.spec.get("sort_by")], ascending=self.spec.get("ascending"))


class LineChartAsset(Asset):

    def display(self):
        data = self.fetch_metric_data()
        data = self.sort_metric_data(data)
        streamlit.line_chart(data, x=self.spec.get("x"), y=self.spec.get("y"))


class TableAsset(Asset):

    def display(self):
        data = self.fetch_metric_data()
        data = self.sort_metric_data(data)
        print(data)
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
        return context

    def _load_cache(self):
        return Cache()

    def run(self):
        # Generate dashboard objects
        pages = dict()
        for idx, dashboard_spec in enumerate(self.ctx.get("dashboards")):
            package_name = dashboard_spec.get("package_name")
            assets = list()
            pages[package_name] = (idx, assets)
            for asset_spec in dashboard_spec.get("assets"):
                asset = AssetStreamlitChartMap.chart.get(asset_spec.get("type"))
                assets.append(asset(self.cache, dashboard_spec, asset_spec))

        # Display sidebar
        packages = [dashboard.get("package_name") for dashboard in self.ctx.get("dashboards")]
        with streamlit.sidebar:
            streamlit.title("dbt Dashboards")
            streamlit.subheader("A central place for all your dbt related metrics.")
            option = streamlit.selectbox("Select a dbt package from the list below.", packages)

        # Dsplay selected dashboard
        dashboard_idx, assets = pages.get(option)
        dashboard_spec = self.ctx.get("dashboards")[dashboard_idx]

        streamlit.title(dashboard_spec.get("name"))
        streamlit.text(dashboard_spec.get("description"))
        for asset in assets:
            streamlit.header(asset.spec.get("title"))
            streamlit.text(asset.spec.get("description"))
            asset.display()
            streamlit.divider()


if __name__ == '__main__':
    App().run()
