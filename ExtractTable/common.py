"""
Preprocess the output received from server and interface as a final result to the client
"""
import os
import tempfile
import warnings

import pandas as pd


class ConvertTo:
    """Convert tabular JSON to an user requested output format"""
    FORMATS = {"df", "dataframe", "json", "csv", "dict"}
    DEFAULT = "df"

    def __init__(self, data: dict, fmt: str = DEFAULT, index: bool = False):
        """

        :param data: Tabular JSON data from server
        :param fmt: format to be converted into
        :param index: row index consideration in the output
        """
        self.data = data
        self.output = self._converter(fmt.lower(), index=index)

    def _converter(self, fmt: str, index: bool = False) -> list:
        """
        Actual conversion takes place here using Pandas
        :param fmt: format to be converted into
        :param index: row index consideration in the output
        :return: list of tables from converted into the requested output format
        """
        # To convert the column indices to int to maintain the correct order on a table with more than 9 columns
        dfs = [pd.DataFrame.from_dict(
            {int(k): v for k, v in table["TableJson"].items()}, orient="index"
        ) for table in self.data["Tables"]]
        if fmt in ("df", "dataframe"):
            return dfs
        elif fmt == "dict":
            return [df.to_dict() for df in dfs]
        elif fmt == "csv":
            save_folder = tempfile.mkdtemp()
            output_location = []
            for tbl_n, df in enumerate(dfs):
                csv_name = os.path.join(save_folder, f"_table_{tbl_n+1}.csv")
                df.to_csv(csv_name, index=index)
                output_location.append(csv_name)
            return output_location
        elif fmt == "json":
            return [df.to_json() for df in dfs]
        else:
            warn_msg = f"Supported output formats {self.FORMATS} only. Assigned to default: {self.DEFAULT}"
            warnings.warn(warn_msg)
            return dfs
