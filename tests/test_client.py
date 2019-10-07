import io

import pytest

from ExtractTable.client import ExtractTable
from ExtractTable.common import UsageStats
from ExtractTable.exceptions import ServiceError
from tests.constants import API_KEY, FILE_PATH, RESULTS_FOLDER


@pytest.fixture
def client():
    return ExtractTable(API_KEY)


def test_process_file(client: ExtractTable):
    assert not (client.process_file(FILE_PATH, RESULTS_FOLDER))


def test_process_file_index(client: ExtractTable):
    assert not (client.process_file(FILE_PATH, RESULTS_FOLDER, True))


def test_check_usage(client: ExtractTable):
    assert isinstance(client.check_usage(), UsageStats)


def test_trigger_process_fail(client: ExtractTable):
    with pytest.raises(ServiceError):
        client.trigger_process(io.BytesIO())


def test_get_result_fail(client: ExtractTable):
    with pytest.raises(ServiceError):
        assert client.get_result('')


