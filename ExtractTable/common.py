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
    FORMATS = {"df", "dataframe", "json", "csv", "dict", "xlsx", "excel"}
    DEFAULT = "df"

    def __init__(self, server_response: dict, output_format: str = DEFAULT, indexing: bool = False, table_obj="TableJson"):
        """
        Convert the server response to an user requested output format on Tables
        :param server_response: Tabular JSON data from server
        :param output_format: format to be converted into
        :param indexing: row & column index consideration in the output
        """
        self.server_response = server_response
        self.output = self._converter(output_format.lower(), indexing=indexing, table_obj=table_obj)

    def _converter(self, fmt: str, indexing: bool = False, table_obj="TableJson") -> list:
        """
        Actual conversion takes place here using Pandas
        :param fmt: format to be converted into
        :param indexing: row index consideration in the output
        :return: list of tables from converted into the requested output format
        """
        dfs = []
        for table in self.server_response.get("Tables", []):
            tmp = {int(k): v for k, v in table[table_obj].items()}
            # To convert column indices to int to maintain the table order with more than 9 columns
            cols = [str(x) for x in sorted([int(x) for x in tmp[0]])] if tmp else None
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
        elif fmt in ("xlsx", "excel"):
            output_excel_location = os.path.join(tempfile.mkdtemp(), f"_tables_{len(dfs)}.xlsx")
            if len(dfs) >= 10:
                warnings.warn(f"There are {dfs} tables extracted. Consider to change the output_format to 'csv' instead")
            with pd.ExcelWriter(output_excel_location) as writer:
                for n, df in enumerate(dfs):
                    df.to_excel(writer, f'table_{n+1}', index=indexing, header=indexing)
                writer.save()
            return [output_excel_location]
        elif fmt == "json":
            return [df.to_json() for df in dfs]
        else:
            warn_msg = f"Supported output formats {self.FORMATS} only. Assigned to default: {self.DEFAULT}"
            warnings.warn(warn_msg)
            return dfs


class MakeCorrections:
    def __init__(self, et_resp: dict = None, dataframes: List[pd.DataFrame] = None):
        """
        To apply post processing techniques on the output
        :param et_resp: ExtractTable response
        :param dataframes: user preferred dataframe(s).
            Default assumes all dataframes from the extracttable response, `et_resp`.
            If both `et_resp` and `dataframes` are provided, the later is considered for the processing
        """
        if et_resp:
            self.dataframes = ConvertTo(server_response=et_resp).output

        if not et_resp:
            try:
                self.dataframes = self.__isacceptable__(dataframes)
            except ValueError:
                raise ValueError("Either ExtractTable response or your preferred list of pandas dataframes is required")

    @staticmethod
    def __isacceptable__(dfs) -> List[pd.DataFrame]:
        """Validate the `dataframes` param"""
        if type(dfs) is list:
            if all([type(df) is pd.DataFrame for df in dfs]):
                return dfs
        elif type(dfs) is pd.DataFrame:
            return [dfs]
        raise ValueError("Dataframes should be list of dataframes or a dataframe")

    def split_merged_rows(self) -> List[pd.DataFrame]:
        """
        To split the merged rows into possible multiple rows
        :return: reformatted list of dataframes
        """
        for df_idx, each_df in enumerate(self.dataframes):
            reformat = []
            for row in each_df.to_numpy():
                row = list(row)

                # looks like line separator is " "
                seperators = [col.strip().count(" ") for col in row]
                # Statistical mode to assume the number of rows merged
                mode_ = mode(seperators)

                if mode_:
                    # split the merged rows inside the col
                    tmp = [col.strip().split(' ', mode_) for col in row]
                    for idx in range(len(tmp[0])):
                        tmp_ = []
                        for x in range(len(tmp)):
                            try:
                                val = tmp[x][idx]
                            except IndexError:
                                val = ""
                            tmp_.append(val)
                        reformat.append(tmp_)
                else:
                    reformat.append(row)

            self.dataframes[df_idx] = pd.DataFrame(reformat)

        return self.dataframes

    def split_merged_columns(self, columns_idx: List[int] = None, force_split: bool = False) -> List[pd.DataFrame]:
        """
        To split the merged columns into possible multiple columns
        :param columns_idx: user preferred columns indices.
                Default loops through all columns to find numeric or decimal columns
        :param force_split: To force split through the columns
        :return: reformatted list of dataframes
        """
        # TODO: Should we consider delimiter_pattern for the split?
        for df_idx, df in enumerate(self.dataframes):
            if not columns_idx:
                columns_idx = df.columns

            columns_idx = [str(x) for x in columns_idx]
            reformat = []
            for col_idx in columns_idx:
                tmp = df[col_idx].str.split(expand=True)

                if not any([not any(tmp.isna().any()), force_split]) or tmp.shape[-1] == 1:
                    reformat.append(df[col_idx].tolist())
                    # If user wanted force_split or the split columns have all cell values
                    # then proceed next
                else:
                    reformat.extend([tmp[each].tolist() for each in tmp.columns])

            self.dataframes[df_idx] = pd.DataFrame(reformat).T

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
        if decimal_position > 0:
            thou_regex = reg_ + '(?=.*' + reg_ + ')'
        else:
            thou_regex = reg_
        decimal_position = int(decimal_position)

        for df_idx, df in enumerate(self.dataframes):
            if not columns_idx:
                columns_idx = df.columns
            columns_idx = [str(x) for x in columns_idx]

            for col_idx in columns_idx:
                digits = df[col_idx].str.count(pat=r'\d').sum()
                chars = df[col_idx].str.count(pat=r'[\w]').sum()

                if digits/chars < 0.75:
                    # To infer a numeric or float column
                    # Check if the column contains more digits or characters
                    continue

                df[col_idx] = df[col_idx].str.strip()
                df[col_idx].replace(regex={r'%s' % thou_regex: thousands_separator}, inplace=True)

                # To correct decimal position
                if not decimal_position > 0:
                    continue

                for i, _ in enumerate(df[col_idx]):
                    if not len(df[col_idx][i]) > decimal_position:
                        # length of atleast decimal_position
                        continue
                    elif df[col_idx][i][-(decimal_position+1)] == decimal_separator:
                        # nothing to do if decimal separator already in place
                        continue

                    # If decimal position is a not alphanumeric
                    if re.search(r'\W+', df[col_idx][i][-(decimal_position+1)]):
                        digits = len(re.findall(r'\d', df[col_idx][i]))
                        if digits/len(df[col_idx][i]) >= 0.5:
                            df[col_idx][i] = df[col_idx][i][:-(decimal_position+1)] + decimal_separator + df[col_idx][i][-decimal_position:]

            self.dataframes[df_idx] = df
        return self.dataframes

    def fix_date_format(self, columns_idx: List[int] = None, delimiter: str = "/"):
        """
        To fix date formats of the column
        Eg: 12|1212020 as 12/12/2020
        :param columns_idx: user preferred columns indices.
                Default loops through all columns to find Date Columns
        :param delimiter: "/" or "-" whatelse you prefer
        :return: correted list of dataframes
        """
        date_regex = r'(\d{2}(\d{2})?)(\W)(\d{2}|[A-Za-z]{3,9})(\W)(\d{2}(\d{2})?)\b'
        for df_idx, df in enumerate(self.dataframes):
            if not columns_idx:
                columns_idx = df.columns
            columns_idx = [str(x) for x in columns_idx]

            for col_idx in columns_idx:
                dates = df[col_idx].str.count(pat=date_regex).sum()

                if not (dates >= len(df) * 0.75):
                    # To infer a date column
                    # Check if the column contains digits and non-alpha character greater than column length
                    continue

                df[col_idx] = df[col_idx].str.strip()
                df[col_idx].replace(regex={date_regex: r'\1%s\4%s\6' % (delimiter, delimiter)}, inplace=True)

            self.dataframes[df_idx] = df

        return self.dataframes
