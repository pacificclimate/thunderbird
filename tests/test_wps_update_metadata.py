import pytest

from pywps import Service
from pywps.tests import assert_response_success

from .common import client_for, TESTDATA
from thunderbird.processes.wps_update_metadata import UpdateMetadata
import owslib.wps


@pytest.mark.online
@pytest.mark.parametrize(
    ("opendap", "updates"), 
    [
        (TESTDATA["test_opendap"], "./metadata-conversion/simple_conversion/modify_history.yaml"),
    ],
)

def test_wps_update_metadata_opendap(opendap, kwargs):
    client = client_for(Service(processes=[UpdateMetadata()]))
    datainputs = (
        "opendap=@xlink:href={0};"
        "updates={updates};"
    ).format(opendap, **kwargs)

    resp = client.get(
        service="wps",
        request="Execute",
        version="1.0.0",
        identifier="update_metadata",
        datainputs=datainputs,
    )

    assert_response_success(resp)