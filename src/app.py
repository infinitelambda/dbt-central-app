from src.utils.assets import AssetStreamlitChartMap
from src.utils.cache import Cache
from src.utils.utils import YamlParser, DashboardFinder

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
        # TODO: Decide on caching approach
        return Cache()

    def run(self):
        # Generate dashboard objects
        pages = dict()
        # loops through each parsed file found in directory
        for idx, dashboard_spec in enumerate(self.ctx):
            print(f"self.ctx: {self.ctx}")
            package_name = dashboard_spec.get("package_name")
            assets = list()
            pages[package_name] = (idx, assets)
            print(f"pages: {pages}")
            for asset_spec in dashboard_spec.get("assets"):
                asset = AssetStreamlitChartMap.chart.get(asset_spec.get("type"))
                assets.append(asset(self.cache, dashboard_spec, asset_spec))
                print(f"assets: {assets}")

        # Display sidebar
        packages = [dashboard.get("package_name") for dashboard in self.ctx]
        print(f"\npackages: {packages}")
        with streamlit.sidebar:
            streamlit.title("dbt Dashboards")
            streamlit.subheader("A central place for all your dbt related metrics.")
            option = streamlit.selectbox("Select a dbt package from the list below.", packages)

        # Display dashboard selected by the sidebar
        dashboard_idx, assets = pages.get(option)
        print(f"\ndashboard_idx: {dashboard_idx}")
        print(f"assets display: {assets}")
        dashboard_spec = self.ctx[dashboard_idx]
        print(f"dashboard_spec display: {dashboard_spec}")
        # Main display
        streamlit.title(dashboard_spec.get("name"))  # dashboard name
        streamlit.text(dashboard_spec.get("description"))  # dashboard description
        for asset in assets:
            streamlit.header(asset.spec.get("title"))
            streamlit.markdown(asset.spec.get("description"))
            asset.display()
            streamlit.divider()


if __name__ == '__main__':
    App().run()
