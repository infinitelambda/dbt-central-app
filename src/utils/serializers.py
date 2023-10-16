from typing import List, Tuple, Union

import re


class AssetSerializer(object):
    def __init__(self, asset_dict: dict):
        self.asset_name = None
        self.metric_name = None
        self.group_by = None
        self.limit_rows = None
        self.order_by = None
        self.where_clause = None

        self.api_call_type_asset = False

        self._initialize_values(asset_dict)

    def _initialize_values(self, asset_dict: dict) -> None:
        """
        Extracts relevant asset information and populates to current class instance

            Parameters:
                asset_dict (dict): Asset dictionary to be serialized
        """
        self.asset_name = self.to_snakecase(asset_dict.get("name", ""))
        self.metric_name = asset_dict.get("metric")

        if self.is_valid():
            self.group_by = asset_dict.get("group by")
            self.limit_rows = asset_dict.get("limit")
            self.order_by = self.compute_order(asset_dict=asset_dict)
            self.where_clause = asset_dict.get("where")

    def is_valid(self) -> bool:
        """
        Check if asset object is valid - confirm presence of asset_name, metric_name
        and that metric_name is a string

            Returns:
                valid (bool): Assestment if asset is valid or not
        """
        valid = False

        if self.asset_name and self.metric_name and type(self.metric_name) == str:
            valid = True

        return valid

    def compute_order(self, asset_dict: dict) -> str:
        """
        Function used to factor in two different ordering mechanisms - sort_by and order
            Parameters:
                asset_dict (dict): Asset dictionary to be serialized

            Returns:
                ordering (str): String to use in order statement
        """
        descending_prefix = "-"
        ordering = asset_dict.get("order", None)

        # Let's try to get the "sort_by" value in case ordering is missing
        if ordering == None:
            ordering = asset_dict.get("sort_by", None)

            # Account for multiple values
            if ordering:
                ordering = ordering.split(",")

                # Accound to descending if passed
                if not asset_dict.get("ascending", True):
                    ordering = [descending_prefix + order for order in ordering]

                ordering = ",".join(ordering)

        return ordering

    def to_snakecase(self, to_snake_case: str) -> str:
        """
        Transforms a string to adhere to snakecase ruleset

            Parameters:
                to_snake_case (str): String to be transformed to camel_case

            Returns:
                snake_cased (str): snake_cased string
        """
        snake_cased = re.sub(r"[\s-]+", "_", to_snake_case.lower())
        return snake_cased

    def generate_mf_query_command(self) -> List[str]:
        """
        Returns an mf query command to be executed when downloading cached files

            Returns:
                commands (List[str]): mf query command list
        """
        command = ["mf", "query", "--metrics", self.metric_name]

        if self.group_by is not None:
            command.extend(["--group-by", self.group_by])

        if self.limit_rows is not None:
            command.extend(["--limit", self.limit_rows])

        if self.order_by is not None:
            command.extend(["--order", self.order_by])

        if self.where_clause is not None:
            command.extend(["--where", self.where_clause])

        return command
