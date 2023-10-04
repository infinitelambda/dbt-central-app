import os

from utils.semantic import SemanticHelper

from collections import Counter

from utils.assets import AssetStreamlitChartMap, IndicatorAsset, Asset
from utils.cache import Cache
from utils.utils import YamlParser, DashboardFinder

import streamlit as st
from streamlit_option_menu import option_menu


class App:
    def __init__(self):
        self.ctx = self._load_context()
        self.cache = self._load_cache()
        self.semantic_api = self._load_semantic_api()

    def _load_context(self):
        finder = DashboardFinder()
        dashboards_path = finder.find_dashboards_dir()
        parser = YamlParser(dashboards_path)
        context = parser.get_raw_data()
        return context

    def _load_cache(self):
        return Cache()


    def _load_semantic_api(self):
        url = os.environ.get("DBT_SEMANTIC_URL")
        if url:
            return SemanticHelper(url=url)
        return None

    # Define a custom sorting key function
    def custom_sort_key(self, asset: Asset) -> int:
        # Assign a lower sort value (0) to IndicatorAsset objects and a higher value (1) to others
        if isinstance(asset, IndicatorAsset):
            return 0
        else:
            return 1


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
                assets.append(asset(self.cache, dashboard_spec, asset_spec, self.semantic_api))

        # Layout
        st.set_page_config(
            page_title="DasboarDBT",
            layout="wide",
            initial_sidebar_state="expanded")

        with st.sidebar:
            selected = option_menu('DashboarDBT', ["Home", 'Dashboards', 'About'],
                                   icons=['house', 'search', 'info-circle'],
                                   menu_icon='clipboard2-data', default_index=0)

        def get_package_option_display(package_name):
            find_package = [
                dashboard.get("name")
                for dashboard in self.ctx
                if dashboard.get("package_name") == package_name
            ]
            if find_package:
                return find_package[0]
            return package_name

        if selected == "Home":
            # Header
            st.title('Welcome to DashboarDBT')
            st.subheader('*A central place for all your dbt related metrics.*')

            st.divider()

            # Use Cases
            with st.container():
                col1, col2 = st.columns(2)
                with col1:
                    st.header('Use Cases')
                    st.markdown(
                        """
                        - _Interested in dashboards which contains information about KPIs?_
                        - _In need of help to monitor Snowflake performance and costs?_
                        - _Evaluating the visualisation of test results?_
                        - _Just here to play and learn?_
                        """
                    )
                with col2:
                    pass

            st.divider()
            with st.container():
                col1, col2, col3 = st.columns([2.2, 1.4, 1.6])
                with col1:
                    st.image('./images/IL_Logo_white.png', width=180)
                with col2:
                    st.image('./images/dbt-png.png', width=83)
                with col3:
                    st.image('./images/Snowflake_Logo.svg.png', width=320)

        # Dashboards menu
        if selected == "Dashboards":
            # Display sidebar
            packages = [dashboard.get("package_name") for dashboard in self.ctx]

            packages.sort()
            dash_sidebar = st.sidebar
            with dash_sidebar:
                option = st.selectbox(
                    "Select a dbt package from the list below.",
                    options=packages,
                    format_func=get_package_option_display,
                )

                st.write('')  # for vertical positioning
                st.write('')
                st.write('')
                st.write('')
                st.write('')
                st.write('')
                st.write('')
                st.write('')
                st.write('')
                st.write('')
                st.write('')
                st.write('')
                col1, col2, col3 = st.columns([2.2, 1.5, 1.5])
                with col1:
                    st.image('./images/IL_Logo_white.png', width=95)
                with col2:
                    st.image('./images/dbt-png.png', width=40)
                with col3:
                    st.image('./images/snowflake.png', width=40)

            # Display dashboard selected by the sidebar
            dashboard_idx, assets = pages.get(option)
            dashboard_spec = self.ctx[dashboard_idx]
            st.title(dashboard_spec.get("name"))  # dashboard name
            st.markdown(dashboard_spec.get("description"))  # dashboard description

            sorted_assets = sorted(assets, key=self.custom_sort_key)  # get line assets first
            num_of_columns = Counter(isinstance(asset, IndicatorAsset) for asset in sorted_assets)[True]
            if num_of_columns > 0:
                st.write("#")  # spacer for UI
                cols = st.columns(num_of_columns)
            for idc, asset in enumerate(sorted_assets):
                if isinstance(asset, IndicatorAsset) and idc <= num_of_columns and num_of_columns > 0:
                    with cols[idc]:
                        asset.display()
                else:
                    st.divider()
                    st.header(asset.spec.get("title"))  # un-indent to see indicators vertically as well
                    st.markdown(asset.spec.get("description"))
                    asset.display()


        # About Page
        if selected == 'About':
            dash_sidebar = st.sidebar
            with dash_sidebar:
                st.write('')  # for vertical positioning
                st.write('')
                st.write('')
                st.write('')
                st.write('')
                st.write('')
                st.write('')
                st.write('')
                st.write('')
                st.write('')
                st.write('')
                st.write('')
                col1, col2, col3 = st.columns([2.2, 1.5, 1.5])
                with col1:
                    st.image('./images/IL_Logo_white.png', width=95)
                with col2:
                    st.image('./images/dbt-png.png', width=40)
                with col3:
                    st.image('./images/snowflake.png', width=40)

            st.title('Presenter')
            with st.container():
                col1, col2 = st.columns(2)
                col1.write('')
                col1.write('')
                col1.write('')
                col1.write('**Name:**    Adrien Boutreau')
                col1.write('**Education:**    Very cool')
                col1.write('**Experience:**    Realllly much')
                col1.write(
                    '**Contact:**    adrien@infinitelambda.com or [linkedin](https://fr.linkedin.com/in/adrien-boutreau)')
                col1.write('**Thanks for stopping by!**')
                col2.image('./images/adrien.jpeg')


if __name__ == '__main__':
    App().run()
