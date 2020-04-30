"""
Purpose: To parse and validate all Server Responses
"""
import warnings

import requests as rq

from .exceptions import ServiceError


class ValidateResponse:
    """Raise custom errors"""
    def __init__(self, resp: rq.Response, show_warn: bool = True):
        """
        Validate the response here
        :param resp: Response from the server
        :param show_warn: Whether to show warning or not
        """
        self.resp = resp
        self.show_warn = show_warn
        self.raise_error()

    def raise_error(self):
        """Check for respone `status_code` to differentiate success and everything else"""
        if self.resp.status_code in (200, 202):
            return
        elif self.resp.status_code in range(200, 206):
            self.show_warnings()
            return
        raise ServiceError(dict_resp=self.resp.json())

    def show_warnings(self):
        """Show Warnings based on `M(m)essage` from the request"""
        if not self.show_warn:
            return
        _msg_ = ''
        if self.resp.json().get('Message', ''):
            _msg_ = self.resp.json()['Message']
        else:
            _msg_ = self.resp.json().get('message', '')

        if _msg_:
            warnings.warn(_msg_)
