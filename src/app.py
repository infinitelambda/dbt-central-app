from utils.assets import AssetStreamlitChartMap
from utils.cache import Cache
from utils.utils import YamlParser, DashboardFinder

import streamlit


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
        return Cache()

    def run(self):
        # Generate dashboard objects
        pages = dict()
        # loops through each parsed file found in directory
        for idx, dashboard_spec in enumerate(self.ctx):
            package_name = dashboard_spec.get("package_name")
            assets = list()
            pages[package_name] = (idx, assets)
            for asset_spec in dashboard_spec.get("assets"):
                asset = AssetStreamlitChartMap.chart.get(asset_spec.get("type"))
                assets.append(asset(self.cache, dashboard_spec, asset_spec))

        # Display sidebar
        def get_package_option_display(package_name):
            find_package = [
                dashboard.get("name")
                for dashboard in self.ctx
                if dashboard.get("package_name") == package_name
            ]
            if find_package:
                return find_package[0]
            return package_name

        packages = [dashboard.get("package_name") for dashboard in self.ctx]
        with streamlit.sidebar:
            streamlit.title("dbt Dashboards")
            streamlit.subheader("A central place for all your dbt related metrics.")
            option = streamlit.selectbox(
                "Select a dbt package from the list below.",
                options=packages,
                format_func=get_package_option_display,
            )

        # Display dashboard selected by the sidebar
        dashboard_idx, assets = pages.get(option)
        dashboard_spec = self.ctx[dashboard_idx]
        streamlit.title(dashboard_spec.get("name"))  # dashboard name
        streamlit.markdown(dashboard_spec.get("description"))  # dashboard description
        for asset in assets:
            streamlit.header(asset.spec.get("title"))
            streamlit.markdown(asset.spec.get("description"))
            asset.display()
            streamlit.divider()


if __name__ == "__main__":
    App().run()
