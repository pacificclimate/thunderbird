import pytest

from pywps import Service
from pywps.tests import assert_response_success

from .common import client_for, TESTDATA
from thunderbird.processes.wps_update_metadata import UpdateMetadata
import owslib.wps
import os

@pytest.mark.online
@pytest.mark.parametrize(
    ("opendap"), [(TESTDATA["test_opendap"])],
)
@pytest.mark.parametrize(
    ("updates"), 
    [
        (os.getcwd()+"/tests/metadata-conversion/updates-CLIMDEX-downscale-BCCAQ.yaml"),
        (os.getcwd()+"/tests/metadata-conversion/updates-downscaled.yaml"),
        (os.getcwd()+"/tests/metadata-conversion/updates-downscaled-climo.yaml"),
        (os.getcwd()+"/tests/metadata-conversion/updates-hydromodel-dgcm.yaml"),
        ("""
global:
    history: "today is a nice day"
        """)
    ],
)
def test_wps_update_metadata_opendap(opendap, updates):
    client = client_for(Service(processes=[UpdateMetadata()]))
    datainputs = (
        "opendap=@xlink:href={0};"
        "updates={1};"
    ).format(opendap, updates)

    resp = client.get(
        service="wps",
        request="Execute",
        version="1.0.0",
        identifier="update_metadata",
        datainputs=datainputs,
    )
    print(resp)
    assert_response_success(resp)