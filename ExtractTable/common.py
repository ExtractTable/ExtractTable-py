"""
Preprocess the output received from server and interface as a final result to the client
"""
import os
import re
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

    def __init__(self, data: dict, fmt: str = DEFAULT, indexing: bool = False, table_obj="TableJson"):
        """

        :param data: Tabular JSON data from server
        :param fmt: format to be converted into
        :param indexing: row & column index consideration in the output
        """
        self.data = data
        self.output = self._converter(fmt.lower(), indexing=indexing, table_obj=table_obj)

    def _converter(self, fmt: str, indexing: bool = False, table_obj="TableJson") -> list:
        """
        Actual conversion takes place here using Pandas
        :param fmt: format to be converted into
        :param indexing: row index consideration in the output
        :return: list of tables from converted into the requested output format
        """
        dfs = []
        for table in self.data.get("Tables", []):
            tmp = {int(k): v for k, v in table[table_obj].items()}
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
    def __init__(self, et_resp: dict, split_merged_rows=False):
        self.et_resp = et_resp
        self.dataframes = ConvertTo(data=et_resp, fmt="df", table_obj="TableJson").output
        if split_merged_rows:
            self.dataframes = self.split_merged_rows()

    def split_merged_rows(self) -> List[pd.DataFrame]:
        """To split the merged rows into possible multiple rows"""
        for df_idx, each_df in enumerate(self.dataframes):
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

            self.dataframes[df_idx] = pd.DataFrame(re_format)

        return self.dataframes

    def fix_decimal_format(self, columns_idx: List[int] = None, decimal_separator: str = ".", thousands_separator: str = ",", decimal_position: int = 2) -> List[pd.DataFrame]:
        """
        To fix decimal and thousands separator values. Often commas as detected as period
        :param columns_idx: user preferred columns indices.
                Default loops through all columns to find numeric or decimal columns
        :param decimal_separator: preferred decimal separator
        :param thousands_separator: preferred thousands separator
        :param decimal_position: preferred decimal position
        :return: corrected list of dataframes
        """
        # TODO: Should we consider only bad confidence values?

        reg_ = f"[{decimal_separator}{thousands_separator}]"
        thou_regex = reg_ + '(?=.*' + reg_ + ')'
        decimal_position = int(decimal_position)

        for df_idx, df in enumerate(self.dataframes):
            if not columns_idx:
                columns_idx = df.columns

            for col_idx in columns_idx:
                digits = sum(df[str(col_idx)].str.count(pat=r'\d'))
                chars = sum(df[str(col_idx)].str.count(pat=r'[\w]'))

                if digits/chars < 0.75:
                    # To infer a numeric or float column
                    # Check if the column contains more digits or characters
                    continue

                df[str(col_idx)] = df[str(col_idx)].str.strip()
                df[str(col_idx)].replace(regex={thou_regex: thousands_separator}, inplace=True)

                for i, _ in enumerate(df[str(col_idx)]):
                    if not len(df[str(col_idx)][i]) > decimal_position:
                        # length of atleast decimal_position
                        continue
                    elif df[str(col_idx)][i][-(decimal_position+1)] == decimal_separator:
                        # nothing to do if decimal separator already in place
                        continue

                    # If decimal position is a not alphanumeric
                    if re.search(r'\W+', df[str(col_idx)][i][-(decimal_position+1)]):
                        digits = len(re.findall(r'\d', df[str(col_idx)][i]))
                        if digits/len(df[str(col_idx)][i]) >= 0.5:
                            df[str(col_idx)][i] = df[str(col_idx)][i][:-(decimal_position+1)] + decimal_separator + df[str(col_idx)][i][-decimal_position:]

            self.dataframes[df_idx] = df
        return self.dataframes

    def fix_date_format(self, columns_idx: List[int] = None):
        """
        To fix date formats of the column
        Eg: 12|1212020 as 12/12/2020
        :param columns_idx: user preferred columns indices.
                Default loops through all columns to find Date Columns
        :return: correted list of dataframes
        """
        return self.dataframes

