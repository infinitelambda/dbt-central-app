import os

from collections import Counter

from utils.assets import AssetStreamlitChartMap, IndicatorAsset, Asset
from utils.cache import Cache
from utils.utils import YamlParser, DashboardFinder, ValidateUserYaml, InvalidYamlSpecification
from utils.data_loader import DataLoader

import streamlit as st
from streamlit_option_menu import option_menu

HOME = "Home"
DATA_LOADER = "Data Loader"
DASHBOARDS = "Dashboards"
CONFIGURATION = "Configuration"
CHANGE_LOG = "Change log"
DOCUMENTATION = "Documentation"


class App:
    def __init__(self):
        self.ctx = self._load_context()
        self.cache = self._load_cache()
        self.validator = ValidateUserYaml()

    def _load_context(self):
        finder = DashboardFinder()
        dashboards_path = finder.find_dashboards_dir()
        parser = YamlParser(dashboards_path)
        context = parser.get_raw_data()
        return context

    def _load_data(self, dbt_path):
        loader = DataLoader()
        loader.load(dbt_path=dbt_path)
        self.loaded_cache = True

    def _load_cache(self):
        return Cache()

    # Define a custom sorting key function
    def custom_sort_key(self, asset: Asset) -> int:
        # Assign a lower sort value (0) to IndicatorAsset objects and a higher value (1) to others
        if isinstance(asset, IndicatorAsset):
            return 0
        else:
            return 1

    def run(self):
        # Layout
        st.set_page_config(
            page_title="dashboardbt", layout="wide", initial_sidebar_state="expanded"
        )

        with st.sidebar:
            selected = option_menu(
                "dashboardbt",
                [
                    HOME,
                    DATA_LOADER,
                    DASHBOARDS,
                    CONFIGURATION,
                    CHANGE_LOG,
                    DOCUMENTATION,
                ],
                icons=[
                    "house",
                    "cloud-download",
                    "search",
                    "gear",
                    "clock-history",
                    "file-text",
                ],
                menu_icon="clipboard2-data",
                default_index=0,
            )

        def get_package_option_display(package_name):
            find_package = [
                dashboard.get("name")
                for dashboard in self.ctx
                if dashboard.get("package_name") == package_name
            ]
            if find_package:
                return find_package[0]
            return package_name

        if selected == HOME:
            # Header
            st.title("Welcome to dashboardbt")
            st.subheader("*A central place for all your dbt related metrics.*")
            st.markdown(
                "Developed by [Infinite Lambda](https://infinitelambda.com/dbt-premier-consulting-partner/) :first_place_medal:"
            )

            st.divider()

            # Use Cases
            with st.container():
                col1, col2 = st.columns(2)
                with col1:
                    st.header("Use Cases")
                    st.markdown(
                        """
                        - _Interested in dashboards which contains information about KPIs?_
                        - _Monitor your dbt jobs & Snowflake costs_
                        - _Evaluating the visualisation of test results?_
                        """
                    )
                    st.header("Your links")
                    st.markdown(
                        """
                        - [dbt cloud jobs](https://cloud.getdbt.com/deploy/11553/projects/290967/jobs)
                        - [dbt cloud docs](https://cloud.getdbt.com/accounts/11553/jobs/419022/docs/#!/overview)
                        - [Snowflake admin](https://app.snowflake.com/gezjpyc/infinitelambda/#/account/usage)
                        - [Link to repository](https://github.com/infinitelambda/central-app-dbt)
                        """
                    )
                with col2:
                    pass

        # Dashboards menu
        if selected == DASHBOARDS:
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
            packages = [dashboard.get("package_name") for dashboard in self.ctx]

            packages.sort()
            dash_sidebar = st.sidebar
            with dash_sidebar:
                option = st.selectbox(
                    "Select a dbt package from the list below.",
                    options=packages,
                    format_func=get_package_option_display,
                )

            # Display dashboard selected by the sidebar
            dashboard_idx, assets = pages.get(option)
            dashboard_spec = self.ctx[dashboard_idx]
            try:
                self.validator.validate_dashboard(dashboard_spec)
            except InvalidYamlSpecification as e:
                st.error(
                    f"Dashboard is missing one of the expected attributes: {e}\n", icon="⚠️"
                )

            st.title(dashboard_spec.get("name"))  # dashboard name
            st.markdown(dashboard_spec.get("description"))  # dashboard description

            sorted_assets = sorted(assets, key=self.custom_sort_key)  # get line assets first
            num_of_columns = Counter(
                isinstance(asset, IndicatorAsset) for asset in sorted_assets
            )[True]
            if num_of_columns > 0:
                st.write("#")  # spacer for UI
                cols = st.columns(4)
            for idc, asset in enumerate(sorted_assets):
                if (
                    isinstance(asset, IndicatorAsset)
                    and idc <= num_of_columns
                    and num_of_columns > 0
                ):
                    with cols[idc % 4]:
                        asset.display()
                else:
                    st.divider()
                    st.header(
                        asset.spec.get("title")
                    )  # un-indent to see indicators vertically as well
                    st.markdown(asset.spec.get("description"))
                    asset.display()

        # Data Loader Menu
        if selected == DATA_LOADER:
            st.title("Data Loader")

            with st.container():
                col1, col2 = st.columns(2)
                with col1:
                    st.header("Loading Cache Data")
                    st.header("Your links")
                    st.markdown(
                        """
                        This page will allow you to generate or regenerate the cache data.

                        Please ensure that before you continue - you have confirmed your dbt project is set up correctly and note the root directory of said project.

                        After you input the _full_ path - click the `Load` and await the completion of the load
                        """
                    )
                with col2:
                    pass

                directory = st.text_input(
                    label="dbt Project Directory 📂",
                    type="default",
                    placeholder="Enter your dbt project dir here",
                )

                def disable_load_button(b):
                    st.session_state["disabled"] = b

                if st.button(
                    "Load",
                    key="load_button",
                    type="primary",
                    on_click=disable_load_button,
                    disabled=st.session_state.get("disabled", False),
                    args=(True,),
                ):
                    # Validate that directory exists
                    if not os.path.isdir(directory):
                        st.text(
                            "Directory {directory} does not exist".format(directory=directory)
                        )
                        return
                    # Validate that dbt_project.yml exists
                    if not os.path.exists(f"{directory.rstrip('/')}/dbt_project.yml"):
                        st.text(
                            "Directory {directory} does not contain dbt_project.yml".format(
                                directory=f"{directory.rstrip('/')}/dbt_project.yml"
                            )
                        )

                    self._load_data(dbt_path=directory)

        # Configuration Page
        if selected == CONFIGURATION:
            st.title("Configuration")

            st.text_input(
                label="dbt Cloud API Key 🔑",
                type="password",
                placeholder="Enter your dbt cloud api key here",
            )

            st.text_input(
                label="dbt Cloud Job ID  🔖", placeholder="Enter dbt Cloud Job ID here"
            )

            st.button("Save", type="primary")

        if selected == CHANGE_LOG:
            st.title("Change log")
            file_path = "../CHANGELOG.md"
            try:
                with open(file_path, "r", encoding="utf-8") as file:
                    readme_contents = file.read()

                    st.markdown(readme_contents)
            except FileNotFoundError:
                print(f"The file '{file_path}' was not found.")
            except Exception as e:
                print(f"An error occurred: {e}")

        if selected == DOCUMENTATION:
            st.title("Documentation")
            file_path = "../README.md"
            try:
                with open(file_path, "r", encoding="utf-8") as file:
                    readme_contents = file.read()

                    st.markdown(readme_contents)
            except FileNotFoundError:
                print(f"The file '{file_path}' was not found.")
            except Exception as e:
                print(f"An error occurred: {e}")


if __name__ == "__main__":
    App().run()
