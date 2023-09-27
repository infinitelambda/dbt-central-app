import abc

import pandas as pd
import streamlit

from src.utils.cache import CacheMiss


class Asset(abc.ABC):
    def __init__(self, cache, dashboard, spec):
        self.cache = cache
        self.dashboard = dashboard
        self.spec = spec

    def fetch_metric_data(self):
        return self.cache.fetch(package=self.dashboard.get("package_name"), metric=self.spec.get("metric"))

    def sort_metric_data(self, data) -> pd.DataFrame:
        data = self.fetch_metric_data()
        return data.sort_values(by=[self.spec.get("sort_by")], ascending=self.spec.get("ascending"))

    def display(self):
        try:
            data = self.fetch_metric_data()
            #  sorted_data = self.sort_metric_data(data)
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
        streamlit.dataframe(data)


class IndicatorAsset(Asset):
    def chart(self, data: pd.DataFrame):
        streamlit.metric(label=str(self.spec.get("title")), value=data.iloc[0, 0])


class AssetStreamlitChartMap:
    chart = {
        "line_chart": LineChartAsset,
        "table": TableAsset,
        "indicator": IndicatorAsset
    }
