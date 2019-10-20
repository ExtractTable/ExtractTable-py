import os
import io

import pytest

from ExtractTable.client import ExtractTable
from ExtractTable.exceptions import ServiceError
from tests.constants import API_KEY, FILE_PATH


@pytest.fixture
def client():
    return ExtractTable(API_KEY)


def test_get_result_fail(client: ExtractTable):
    with pytest.raises(ServiceError):
        assert not client.get_result('')


def test_trigger_process_fail(client: ExtractTable):
    with pytest.raises(ServiceError):
        client.trigger_process(io.BytesIO())


def test_check_usage(client: ExtractTable):
    assert isinstance(client.check_usage(), dict)


def test_process_file(client: ExtractTable):
    assert isinstance(client.process_file(filepath=FILE_PATH, output_format="df"), list)


def test_process_file_csv(client: ExtractTable, fmt="csv"):
    return all([os.path.exists(x) and x.endswith(fmt) for x in client.process_file(filepath=FILE_PATH, output_format=fmt)])
