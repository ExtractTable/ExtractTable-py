"""
Any Request or Response of a transaction must take place here
"""
from urllib import parse as urlparse
import os
import shutil
import typing as ty
from typing import BinaryIO
import time
import warnings

import requests as rq

from .FileOperations import PrepareInput, CheckFile
from .config import HOST, JobStatus
from .parsers import ValidateResponse
from .common import ConvertTo
from .exceptions import ClientFileSizeError


class ExtractTable:
    from .__version__ import __version__
    _OUTPUT_FORMATS: set = ConvertTo.FORMATS
    _DEFAULT: str = ConvertTo.DEFAULT
    _WARNINGS: bool = True
    _WAIT_UNTIL_OUTPUT: bool = True
    VERSION = f"ExtractTable_{__version__}"

    def __init__(self, api_key: str):
        """
        Starts by creating a session
        :param api_key: API Key recieved from https://extracttable.com
        """
        self.api_key = api_key
        self._session = rq.Session()
        self._session.headers['x-api-key'] = self.api_key

        # Helpul if the user wants to dig into the actual server response
        self.ServerResponse = rq.Response

    def _make_request(self, method, host: urlparse, params: dict = None, data: dict = None, **kwargs) -> dict:
        """
        Create a server request and parse the response for validation
        :param method: Request method
        :param host: endpoint to send the request
        :param params: query params for the request
        :param data: form data for the requests
        :param kwargs: Any other that a server accepts
        :return: json response of the server
        """
        tmp = self.__dict__.copy()
        for _type, _obj in tmp.items():
            if _type not in ("api_key", "_session", "input_filename"):
                self.__delattr__(_type)

        host = host if not host.startswith("http") else host.split("/")[2]
        url = urlparse.urlunparse(('https', host, '', '', '', ''))
        self.ServerResponse = self._session.request(method, url, params=params, data=data, **kwargs)
        ValidateResponse(resp=self.ServerResponse, show_warn=self._WARNINGS)
        self.server_response = self.ServerResponse.json()
        return self.ServerResponse.json()

    def check_usage(self) -> dict:
        """
        Check the usage of the API Key is valid
        :return the plan usage of the API Key, if valid
        """
        resp = self._make_request('get', HOST.VALIDATOR)

        return resp['usage']
    
    def view_transactions(self) -> list:
        """
        View your transactions in the past 24 hours
        :return list of transactions; each record with
            JobStatus: Status of the job
            Pages: number of pages of the input; can also be considered as number of credits consumed
            createdon: timestamp when the request was processed
            requested_filename: Filename received in the request
            txn_id: Unique identifier of the transaction, also referred as JobId when retrieving the output via get_result()
        """
        resp = self._make_request("GET", HOST.TRANSACTIONS)
        return resp

    def get_result(self, job_id: str, wait_time: int = 10, max_wait_time: int = 300) -> dict:
        """
        Retrieve the tabular data of a triggered job based on the JobId
        :param job_id: JobId received from an already triggered process
        :param wait_time: Time to wait before making another request
        :param max_wait_time: Maximum Time to wait before returning to the client
        :return: Tabular JSON when processed successful else helpful user info
        """
        params = {'JobId': job_id}
        resp = self._make_request('get', HOST.RESULT, params=params)
        # Loop to retrieve the output until max_wait_time is reached
        max_wait_time = int(max_wait_time)
        while self._WAIT_UNTIL_OUTPUT and resp["JobStatus"] == JobStatus.PROCESSING and max_wait_time > 0:
            time.sleep(max(10, int(wait_time)))
            max_wait_time -= wait_time
            resp = self._make_request('get', HOST.RESULT, params=params)
        
        if resp.get('DownloadUrl', ''):
            self.ServerResponse = rq.get(resp['DownloadUrl'])
            self.server_response = resp = self.ServerResponse.json()

        return resp

    def trigger_process(self, fp: BinaryIO, dup_check: bool = False, **kwargs) -> dict:
        """
        Trigger the document to the server for processing
        :param fp: Binary file data of the input file
        :param dup_check: helps to handle idempotent requests
        :param kwargs: anyother form-data to be sent to the server
        :return: Tabular JSON when processed successful else helpful user info
        """
        max_wait_time = kwargs.pop('max_wait_time', 300)
        data = {'dup_check': dup_check, "library": kwargs.pop("library", self.VERSION)}
        data.update(kwargs)
        if "signed_filename" in data:
            resp = self._make_request('post', HOST.TRIGGER, data=data)
        else:
            resp = self._make_request('post', HOST.TRIGGER, data=data, files={'input': fp})

        # GetResult if JobId is present in the response
        # Usually happens when processing PDF files or idempotent requests
        if 'JobId' in resp and resp.get("JobStatus", "") == JobStatus.PROCESSING:
            if max_wait_time > 0:
                print("[Info]: Waiting to retrieve the output; JobId:", resp['JobId'])
            else:
                print("[Info]: JobId:", resp['JobId'])
            resp = self.get_result(resp['JobId'], max_wait_time=max_wait_time)

        return resp

    def bigfile_upload(self, filepath):
        """
        To aid big file processing by uploading the file first and triggering the process next
        :param filepath: filepath
        :return: a signed URL to upload the file
        """
        resp = self._make_request('post', HOST.BIGFILE, data={"filename": filepath})

        return resp

    def process_file(
            self,
            filepath: ty.Union[str, bytes, os.PathLike],
            pages: ty.Union[str] = "1",
            output_format: str = "df",
            dup_check: bool = False,
            indexing: bool = False,
            **kwargs
    ) -> list:
        """
        Trigge the file for processing and returns the tabular data in the user requested output format
        :param filepath: Location of the file
        :param pages : str, optional (default: '1')
                Comma-separated page numbers.
                Example: '1,3,4' or '1,4-end' or 'all'.
        :param output_format: datafram as default; Check `ExtractTable._OUTPUT_FORMATS` to see available options
        :param dup_check: Idempotent requests handler
        :param indexing: Whether to output row & column indices in the outputs other than df
        :param kwargs:
            max_wait_time: int, optional (default: 300);
                Maximum Time to wait before returning to the client
            any other form-data to be sent to the server for future considerations
        :return: user requested output in list;
        """
        # Raise a warning if unknown format is requested
        if output_format not in self._OUTPUT_FORMATS:
            warn_msg = f"Found: '{output_format}' as output_format; Allowed formats are {self._OUTPUT_FORMATS}. " \
                       f"Assigned to default format: {self._DEFAULT}"
            warnings.warn(warn_msg)

        # To use the reference when saving the output
        self.__setattr__('input_filename', os.path.basename(filepath))

        with PrepareInput(filepath, pages=pages) as infile:
            with open(infile.filepath, 'rb') as fp:
                is_big_file = CheckFile(infile.filepath).is_big
                if not is_big_file:
                    trigger_resp = self.trigger_process(fp, dup_check=dup_check, **kwargs)
                else:
                    big_gen = self.bigfile_upload(filepath=os.path.basename(infile.filepath))
                    with open(infile.filepath, 'rb') as ifile:
                        rq.post(big_gen['url'], data=big_gen['fields'], files={'file': ifile})
                    trigger_resp = self.trigger_process(None, signed_filename=big_gen["fields"]["key"], dup_check=dup_check, **kwargs)

        for _type, _obj in trigger_resp.items():
            self.__setattr__(_type, _obj)

        result = ConvertTo(server_response=trigger_resp, output_format=output_format, indexing=indexing).output
        return result

    def save_output(self, output_folder: os.PathLike = "", output_format: str = "csv", indexing: bool = False):
        """
        Save the objects of session data to user preferred location or a default folder
        :param output_folder: user preferred output location; default tmp directory
        :param output_format: needed only for tables CSV or XLSX
        :param indexing: row & column index consideration in the output
        :return: location of the output
        """
        input_fname = self.input_filename.rsplit('.')[0]

        output_format = output_format.lower()
        if output_format not in ("csv", "xlsx"):
            output_format = "csv"
            warnings.warn("Invalid 'output_format' given. Defaulted to 'csv'")

        table_outputs_path = ConvertTo(server_response=self.server_response, output_format=output_format, indexing=indexing).output

        if output_folder:
            if not os.path.exists(output_folder):
                try:
                    os.mkdir(output_folder)
                except Exception as e:
                    warnings.warn(f"[Warn]: {str(e)}")
                    warnings.warn(f"Failed to created output_folder not exists. Saving the outputs to {output_folder}")
                    output_folder = os.path.dirname(table_outputs_path[0])
        else:
            output_folder = os.path.dirname(table_outputs_path[0])

        if output_folder != os.path.dirname(table_outputs_path[0]):
            for each_tbl_path in table_outputs_path:
                shutil.move(each_tbl_path,
                            os.path.join(output_folder, input_fname + os.path.basename(each_tbl_path)))

        for each_page in self.server_response.get("Lines", []):
            page_txt_fname = os.path.join(output_folder, f"{input_fname}_Page_{str(each_page['Page'])}.txt")
            page_txt = [each_line['Line'] for each_line in each_page['LinesArray']]
            with open(page_txt_fname, "w", encoding="utf-8") as ofile:
                ofile.write("\n".join(page_txt))

        return output_folder
