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


class DynamicAsset(Asset):
    def chart(self, data: pd.DataFrame):
        func = getattr(streamlit, self.spec.get("dynamic_type"))
        spec = self.spec.get("dynamic_spec", {})
        spec_w_data = {}
        for key in spec.keys():
            expressions = spec[key].split(":")
            if expressions[0] == "eval":
                exp = str(expressions[-1])
                exp = exp\
                    .replace("@this", "self.spec")\
                    .replace("@data", "data")
                spec_w_data[key] = eval(exp)
            else:
                spec_w_data[key] = spec[key]
        func(**spec_w_data)


class EvaluatorReportAsset(Asset):
    def get_traffic_light(self, status):
        if status == "PASS":
            return "🟢"
        if status == "WARN":
            return "🟡"
        if status == "FAIL":
            return "🔴"
        return "⌛"
    
    def get_title(self, row, cols=[]):
        return " / ".join([str(row[x]) for x in cols])
    
    def chart(self, data: pd.DataFrame):
        # get spec
        evaluation_spec = self.spec.get("evaluator_report_spec",{})
        assert evaluation_spec != {}, "evaluator_report_spec is not specified"
        
        group_by_cols = evaluation_spec.get("group_by", data.columns.tolist())
        sort_by_cols = evaluation_spec.get("sort_by", list(group_by_cols))
        sort_accendings = evaluation_spec.get("sort_ascending", [True for x in sort_by_cols])
        metric_col = self.spec.get("metric")
            
        row_identifier_by_col = evaluation_spec.get("row_identifier_by")
        assert row_identifier_by_col is not None, "row_identifier_by is not specified"
        row_status_col = evaluation_spec.get("row_status_by", "STATUS")
        assert row_status_col in data, "row_status_by value cannot be found in the data"
        row_title_by_cols = evaluation_spec.get("row_title_by", list(group_by_cols))
        row_doc_by_cols = evaluation_spec.get("row_doc_by", ["DOC"])
        
        # agg data
        data = data.fillna({row_identifier_by_col: ""})
        group_by_cols.insert(0, pd.Categorical(data[metric_col]))
        agg = data.groupby(group_by_cols, observed=True).sum().reset_index()
        agg = agg.sort_values(
            by=sort_by_cols,
            ascending=sort_accendings
        )
        
        # display as list of expanders
        for _, row in agg.iterrows():
            light = self.get_traffic_light(status=row[row_status_col] if row_status_col in agg else "")
            title = self.get_title(row=row, cols=row_title_by_cols)
            
            with streamlit.expander(f"{light} {title} ({row[metric_col]})"):
                for doc in row_doc_by_cols:
                    streamlit.markdown(
                        f"ℹ️ {row[doc]}" if doc in agg 
                        else f"> _⚠️ `{doc}` column is not found in the input data_"
                    )
                    
                streamlit.markdown("**👀 Identifiers of the detected failure(s):**")
                streamlit.dataframe(
                    pd.DataFrame(
                        data=row[row_identifier_by_col].split(","),
                        columns=[row_identifier_by_col]
                    ), 
                    hide_index=True
                )


class AssetStreamlitChartMap:
    chart = {
        "line_chart": LineChartAsset,
        "table": TableAsset,
        "indicator": IndicatorAsset,
        "dynamic": DynamicAsset,
        "evaluator_report": EvaluatorReportAsset
    }