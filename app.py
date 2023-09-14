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
        type: line_chart
        sort_by: TPCH_COUNT_ORDERS
        ascending: True
        x: METRIC_TIME__MONTH
        y: TPCH_COUNT_ORDERS
        metrics:
          - tpch_count_orders
""")


class Cache:
    def __init__(self):
        self.path = ".cache"

    def fetch(self, package, metric):
        return pd.read_csv(Path(self.path, package, metric + ".csv"))


class AssetStreamlitChartMap:
    chart = {
        "line_chart": streamlit.line_chart
    }


class Asset:
    def __init__(self, cache, dashboard, spec):
        self.cache = cache
        self.dashboard = dashboard
        self.spec = spec

    def fetch_metric_data(self):
        # TODO: check we can have only one metric per asset
        # TODO: define logic if multiple metrics
        return self.cache.fetch(package=self.dashboard.get("package_name"), metric=self.spec.get("metrics")[0])

    def display(self):
        data = self.fetch_metric_data()
        data.sort_values(by=self.spec.get("sort_by"), ascending=self.spec.get("ascending"))
        draw_chart = AssetStreamlitChartMap.chart.get(self.spec.get("type"))
        draw_chart(data, x=self.spec.get("x"), y=self.spec.get("y"))


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
        for idx, dashboard in enumerate(self.ctx.get("dashboards")):
            package_name = dashboard.get("package_name")
            assets = list()
            pages[package_name] = (idx, assets)
            for asset in dashboard.get("assets"):
                assets.append(Asset(self.cache, dashboard, asset))

        # Display sidebar
        packages = [dashboard.get("package_name") for dashboard in self.ctx.get("dashboards")]
        with streamlit.sidebar:
            streamlit.title("dbt Dashboards")
            streamlit.subheader("A central place for all your dbt related metrics.")
            option = streamlit.selectbox("Select a dbt package from the list below.", packages)

        # Dsplay selected dashboard
        dashboard_idx, assets = pages.get(option)
        dashboard = self.ctx.get("dashboards")[dashboard_idx]

        streamlit.title(dashboard.get("name"))
        streamlit.text(dashboard.get("description"))
        for asset in assets:
            streamlit.header(asset.spec.get("title"))
            asset.display()
            streamlit.divider()


if __name__ == '__main__':
    App().run()
