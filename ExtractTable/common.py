"""
Preprocess the output received from server and interface as a final result to the client
"""
import os
import tempfile
import warnings
import collections
from statistics import mode
from typing import List

import pandas as pd


class ConvertTo:
    """Convert tabular JSON to an user requested output format"""
    FORMATS = {"df", "dataframe", "json", "csv", "dict"}
    DEFAULT = "df"

    def __init__(self, data: dict, fmt: str = DEFAULT, indexing: bool = False):
        """

        :param data: Tabular JSON data from server
        :param fmt: format to be converted into
        :param indexing: row & column index consideration in the output
        """
        self.data = data
        self.output = self._converter(fmt.lower(), indexing=indexing)

    def _converter(self, fmt: str, indexing: bool = False) -> list:
        """
        Actual conversion takes place here using Pandas
        :param fmt: format to be converted into
        :param indexing: row index consideration in the output
        :return: list of tables from converted into the requested output format
        """
        dfs = []
        for table in self.data.get("Tables", []):
            tmp = {int(k): v for k, v in table["TableJson"].items()}
            # To convert column indices to int to maintain the table order with more than 9 columns
            cols = [str(x) for x in sorted([int(x) for x in tmp[0]])]
            # To convert row indices to int and maintain the table order with more than 9 rows
            tmp = collections.OrderedDict(sorted(tmp.items()))
            dfs.append(pd.DataFrame.from_dict(tmp, orient="index", columns=cols))

        if fmt in ("df", "dataframe"):
            return dfs
        elif fmt == "dict":
            return [df.to_dict() for df in dfs]
        elif fmt == "csv":
            save_folder = tempfile.mkdtemp()
            output_location = []
            for tbl_n, df in enumerate(dfs):
                csv_name = os.path.join(save_folder, f"_table_{tbl_n+1}.csv")
                df.to_csv(csv_name, index=indexing, header=indexing)
                output_location.append(csv_name)
            return output_location
        elif fmt == "json":
            return [df.to_json() for df in dfs]
        else:
            warn_msg = f"Supported output formats {self.FORMATS} only. Assigned to default: {self.DEFAULT}"
            warnings.warn(warn_msg)
            return dfs


class PostProcessing:
    """To apply post processing techniques on the output"""
    def __init__(self, dataframes: List[pd.DataFrame], split_merged_rows=False):
        self.dataframes = dataframes
        if split_merged_rows:
            self.dataframes = self.split_merged_rows(dataframes)

    def split_merged_rows(self, dataframes: List[pd.DataFrame]) -> List[pd.DataFrame]:
        """To split the merged rows into possible multiple rows"""
        for df_idx, each_df in enumerate(dataframes):
            re_format = []
            for row in each_df.to_numpy():
                row = list(row)
                seperators = []
                for col in row:
                    # looks like line separator is " "
                    seperators.append(col.strip().count(" "))
                # Take statistical mode into consideration to assume the number of rows merged
                mode_ = mode(seperators)

                if mode_:
                    tmp = []
                    for col in row:
                        # split the merged rows inside the col
                        tmp.append(col.strip().split(' ', mode_))

                    for idx in range(len(tmp[0])):
                        tmp_ = []
                        for x in range(len(tmp)):
                            try:
                                val = tmp[x][idx]
                            except IndexError:
                                val = ""
                            tmp_.append(val)
                        re_format.append(tmp_)
                else:
                    re_format.append(row)

            dataframes[df_idx] = pd.DataFrame(re_format)

        return dataframes
