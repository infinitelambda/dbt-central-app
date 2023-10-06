import abc
import base64
import os
import string
from dataclasses import dataclass
from enum import Enum
from typing import Union
from urllib.parse import parse_qs, urlparse

import httpx
import pyarrow as pa
import streamlit as st
from adbc_driver_flightsql import DatabaseOptions
from adbc_driver_flightsql.dbapi import connect
from pandas import DataFrame


@dataclass
class SemanticConnectionConfig:
    host_jdbc: str  # "grpc+tls:semantic-layer.cloud.getdbt.com:443"
    host_graphql: str  # "https://semantic-layer.cloud.getdbt.com/api/graphql"
    environment_id: str  # 42
    token: str  # "Bearer dbts_thisismyprivateservicetoken"
    params: dict  # {"environmentId": 42}


class SemanticInvalidURL(Exception):
    pass


class SemanticType(Enum):
    JDBC = "jdbc"
    GRAPHQL = "graphql"


class SingletonABCMeta(abc.ABCMeta):
    """Singleton Metaclass for ABC"""

    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(SingletonABCMeta, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class SemanticAPI(metaclass=SingletonABCMeta):
    """Abstract Semantic Layer API"""

    def __init__(self, url: str) -> None:
        """Parse the JDBC URL and get the API connection

        Args:
            url (str): JDBC URL (aka DBT_SEMANTIC_URL)
                e.g. "jdbc:arrow-flight-sql://host:port?environmentId=?&token=?"
        """
        self.config: SemanticConnectionConfig = self._get_connection_config(url=url)
        self.conn = self.get_connection()

    def _get_connection_config(self, url: str) -> SemanticConnectionConfig:
        """Parse JDBC URL

        Args:
            url (str): JDBC URL

        Returns:
            SemanticConnectionConfig: Contains all info for constructing the API connection
        """
        parsed = urlparse(url)
        params = {k.lower(): v[0] for k, v in parse_qs(parsed.query).items()}

        return SemanticConnectionConfig(
            host_jdbc=str(
                parsed.path.replace("arrow-flight-sql", "grpc")
                if params.pop("useencryption", None) == "false"
                else parsed.path.replace("arrow-flight-sql", "grpc+tls")
            ),
            host_graphql=str(
                parsed.path.replace("arrow-flight-sql", "https").strip(":443")
                + "/api/graphql"
            ),
            environment_id=params.get("environmentid"),
            token=f"Bearer {params.pop('token')}",
            params=params,
        )

    @abc.abstractclassmethod
    def get_connection(self):
        """Get API connection"""
        pass

    @abc.abstractclassmethod
    def query(self, metric: Union[str, dict]) -> DataFrame:
        """Get data based on the metric query

        Args:
            metric (Union[str, dict]): |
                Metric query for API

                For example:
                ```
                metric:
                    query: select * from Golden
                ```

        Returns:
            DataFrame: Data returned
        """
        pass


class SemanticJDBC(SemanticAPI):
    """SemanticJDBC"""

    def __init__(self, url: str) -> None:
        super().__init__(url)

    def get_connection(self):
        try:
            return connect(
                self.config.host_jdbc,
                db_kwargs={
                    DatabaseOptions.AUTHORIZATION_HEADER.value: self.config.token,
                    **{
                        f"{DatabaseOptions.RPC_CALL_HEADER_PREFIX.value}{k}": v
                        for k, v in self.config.params.items()
                    },
                },
                autocommit=True,
            )
        except Exception as e:
            print(str(e))
            return None

    @st.cache_data(hash_funcs={"utils.semantic.SemanticJDBC": type})
    def query(self, metric: Union[str, dict]) -> DataFrame:
        try:
            with self.conn.cursor() as cur:
                if isinstance(metric, dict):
                    cur.execute(operation=metric.get("query"))
                else:
                    cur.execute(
                        operation=f"select * from {{{{ semantic_layer.query(metrics=['{metric}']) }}}}"
                    )
                return cur.fetch_df()
        except Exception as e:
            print(str(e))
            return None


class SemanticGraphQL(SemanticAPI):
    """SemanticGraphQL"""

    def __init__(self, url: str) -> None:
        super().__init__(url)

    def get_connection(self):
        return httpx.Client(http2=True)

    @st.cache_data(hash_funcs={"utils.semantic.SemanticGraphQL": type})
    def query(self, metric: dict) -> DataFrame:
        headers = {"Authorization": f"{self.config.token}"}
        query_id = self._get_query_id(headers=headers, query_config=metric.get("query"))
        if query_id:
            return self._fetch_query_data(headers=headers, query_id=query_id)
        return None

    def _get_query_id(self, headers, query_config):
        mutation_template = string.Template(
            """
            mutation {
                createQuery(
                    environmentId:$environment_id
                    $query_config
                ){
                    queryId
                }
            }
        """
        )
        mutation = mutation_template.substitute(
            query_config=query_config, environment_id=self.config.environment_id
        )
        resp = self.conn.post(
            self.config.host_graphql, json={"query": mutation}, headers=headers
        ).json()

        return resp.get("data", {}).get("createQuery", {}).get("queryId")

    def _fetch_query_data(self, headers, query_id):
        fetch_template = string.Template(
            """{
            query(environmentId:$environment_id, queryId:"$query_id"){
                status
                arrowResult
                error
                queryId
            }
        }"""
        )
        query = fetch_template.substitute(
            query_id=query_id, environment_id=self.config.environment_id
        )
        resp = self.conn.post(
            self.config.host_graphql, json={"query": query}, headers=headers
        ).json()

        status = resp.get("data", {}).get("query", {}).get("status")
        while status and status not in ["SUCCESSFUL", "FAILED"]:
            resp = self.conn.post(
                self.config.host_graphql, json={"query": query}, headers=headers
            ).json()
            status = resp.get("data", {}).get("query", {}).get("status")

        if status == "FAILED":
            return None

        with pa.ipc.open_stream(
            base64.b64decode(resp.get("data", {}).get("query", {}).get("arrowResult"))
        ) as reader:
            arrow_table = pa.Table.from_batches(reader, reader.schema)
        return arrow_table.to_pandas()


class SemanticAPIFactory:
    """Semnatic Layer API Factory"""

    def __init__(self) -> None:
        pass

    def get_connection(self, metric: dict) -> SemanticAPI:
        """Return the API Connection based on the query type

        Args:
            metric (dict): metric query with defined type, 1 of: jdbc, graphql

        Returns:
            SemanticAPI: SemanticJDBC or SemanticGraphQL
        """
        type = metric.get("type", SemanticType.JDBC.value)
        jdbc_url = os.environ.get("DBT_SEMANTIC_URL")

        if type == SemanticType.JDBC.value:
            return SemanticJDBC(url=jdbc_url)

        return SemanticGraphQL(url=jdbc_url)
