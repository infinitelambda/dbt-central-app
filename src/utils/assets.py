import abc
import re

import pandas as pd
import streamlit
from utils.semantic import SemanticAPIFactory

from utils.cache import CacheMiss
from utils.utils import InvalidYamlSpecification, ValidateUserYaml


class Asset(abc.ABC):
    def __init__(self, cache, dashboard, spec):
        self.cache = cache
        self.dashboard = dashboard
        self.spec = spec
        self.semantic_api = None
        self.validator = ValidateUserYaml()

    def fetch_metric_data(self) -> pd.DataFrame:
        if isinstance(self.spec.get("metric"), dict):
            # Only create connection on Dashboard using API
            self.semantic_api = SemanticAPIFactory().get_connection(metric=self.spec.get("metric"))
            return self.fetch_metric_data_by_api()
        
        asset_name = re.sub(r'[\s-]+', '_', self.spec.get("name").lower())  # snake_case formatting
        return self.cache.fetch(package=self.dashboard.get("package_name"), asset_name=asset_name)

    def fetch_metric_data_by_api(self) -> pd.DataFrame:
        return self.semantic_api.query(metric=self.spec.get("metric"))

    def sort_metric_data(self, data) -> pd.DataFrame:
        data = self.fetch_metric_data()
        return data.sort_values(by=[self.spec.get("sort_by")], ascending=self.spec.get("ascending"))

    def display(self):
        try:
            #self._check_attributes()
            self.validator.validate_asset(self.spec)
        except InvalidYamlSpecification as e:
            streamlit.error(f"Asset is missing one of the expected attributes: {e}\n", icon="⚠️")
        try:
            data = self.fetch_metric_data()
            if self.spec.get("ascending"):
                sorted_data = self.sort_metric_data(data)
                data = sorted_data

            self.chart(data)
        except CacheMiss:
            streamlit.warning(f"Could not find data for metric `{self.spec.get('metric')}`.", icon="⚠️")

    @abc.abstractmethod
    def chart(self, data: pd.DataFrame):
        pass


class LineChartAsset(Asset):

    def chart(self, data: pd.DataFrame):
        streamlit.line_chart(data, x=self.spec.get("x"), y=self.spec.get("y"))


class TableAsset(Asset):

    def chart(self, data: pd.DataFrame):
        if self.spec.get("transposed", False):
            streamlit.dataframe(data.transpose())
        else:
            streamlit.dataframe(data)


class IndicatorAsset(Asset):
    def chart(self, data: pd.DataFrame):
        streamlit.metric(label=str(self.spec.get("title")), value=data.iloc[0, 0], label_visibility="visible")


class AssetStreamlitChartMap:
    chart = {
        "line_chart": LineChartAsset,
        "table": TableAsset,
        "indicator": IndicatorAsset
    }
