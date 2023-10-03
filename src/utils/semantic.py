from enum import Enum
from typing import Union
from pandas import DataFrame
from dataclasses import dataclass
from urllib.parse import parse_qs, urlparse
from adbc_driver_flightsql import DatabaseOptions
from adbc_driver_flightsql.dbapi import connect
import streamlit as st


@dataclass
class SemanticConnection:
    host: str  # "grpc+tls:semantic-layer.cloud.getdbt.com:443"
    params: dict  # {"environmentId": 42}
    auth_header: str  # "Bearer dbts_thisismyprivateservicetoken"


class SemanticInvalidURL(Exception):
    pass


class SemanticNotImplemented(Exception):
    pass


class SemanticType(Enum):
    JDBC = "jdbc"
    GRAPHQL = "graphql"


class SemanticHelper:
    def __init__(self, url: str) -> None:
        """Initilization

        Args:
            url (str): Semantic API URL

        Raises:
            SemanticNotImplemented: SemanticNotImplemented
            SemanticInvalidURL: SemanticInvalidURL
        """
        if url.startswith("jdbc:"):
            self.conn = self._get_jdbc_conn(jdbc_url=url)
            self.type = SemanticType.JDBC
        elif url.endswith("graphql"):
            # https://semantic-layer.cloud.getdbt.com/api/graphql
            raise SemanticNotImplemented()
        else:
            raise SemanticInvalidURL()

    def _get_jdbc_conn(self, jdbc_url: str) -> SemanticConnection:
        """Get SemanticConnection from JDBC URL

        Args:
            jdbc_url (str): >
                JDBC URL
                e.g. jdbc:arrow-flight-sql://semantic-layer.cloud.getdbt.com:443?environmentId=?&token=?

        Returns:
            SemanticConnection: Object for Semantic API connection
        """
        parsed = urlparse(jdbc_url)
        params = {k.lower(): v[0] for k, v in parse_qs(parsed.query).items()}

        return SemanticConnection(
            host=parsed.path.replace("arrow-flight-sql", "grpc")
            if params.pop("useencryption", None) == "false"
            else parsed.path.replace("arrow-flight-sql", "grpc+tls"),
            params=params,
            auth_header=f"Bearer {params.pop('token')}",
        )

    @st.cache_data(hash_funcs={"utils.semantic.SemanticHelper": type})
    def query(self, metric: Union[str, dict]) -> DataFrame:
        """Sematic layer query

        Args:
            metric (str): Metric name or Semantic query which can be JDBC or GraphQL

        Returns:
            DataFrame: Result of the query. None if having an exception
        """
        return getattr(self, f"{self.type.value}_query".lower())(metric=metric)

    def jdbc_query(self, metric: Union[str, dict]) -> DataFrame:
        """Sematic layer query using JDBC API

        Args:
            metric (Union[str, dict]): |
                Semantic query
                e.g. 'select * from {{ semantic_layer.query(metrics=["test_count"]) }}'

                Or just the metric name e.g. test_count

        Returns:
            DataFrame: Result of the query. None if having an exception
        """
        try:
            with connect(
                self.conn.host,
                db_kwargs={
                    DatabaseOptions.AUTHORIZATION_HEADER.value: self.conn.auth_header,
                    **{
                        f"{DatabaseOptions.RPC_CALL_HEADER_PREFIX.value}{k}": v
                        for k, v in self.conn.params.items()
                    },
                },
            ) as conn, conn.cursor() as cur:
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
