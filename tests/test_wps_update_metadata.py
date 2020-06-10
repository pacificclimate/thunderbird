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
    ("updates"), TESTDATA["test_yaml"],
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

    assert_response_success(resp)


@pytest.mark.parametrize(
    ("netcdf"), TESTDATA["test_local_nc"],
)
@pytest.mark.parametrize(
    ("updates"), TESTDATA["test_yaml"],
)
def test_wps_update_metadata_netcdf(netcdf, updates):
    client = client_for(Service(processes=[UpdateMetadata()]))
    datainputs = (
        "netcdf=@xlink:href={0};"
        "updates={1};"
    ).format(netcdf, updates)

    resp = client.get(
        service="wps",
        request="Execute",
        version="1.0.0",
        identifier="update_metadata",
        datainputs=datainputs,
    )

    assert_response_success(resp)