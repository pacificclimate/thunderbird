import pytest

from pywps import Service
from pywps.tests import assert_response_success

from .common import client_for, TESTDATA
from thunderbird.processes.wps_decompose_flow_vectors import DecomposeFlowVectors
import owslib.wps
import os

@pytest.mark.online
@pytest.mark.parametrize(
    ("opendap"), [(TESTDATA["test_vector_flow"]["opendap"])],
)
@pytest.mark.parametrize(
    ("kwargs"),
    [
        (
            {
                "dest_file": "output.nc",
                "variable": "Flow_Direction",
            }
        ),
    ],
)
def test_wps_decompose_flow_vectors_opendap(opendap, kwargs):
    client = client_for(Service(processes=[DecomposeFlowVectors()]))
    datainputs = (
        "opendap=@xlink:href={0};"
        "dest_file={dest_file};"
        "variable={variable};"
    ).format(opendap, **kwargs)

    resp = client.get(
        service="wps",
        request="Execute",
        version="1.0.0",
        identifier="decompose_flow_vectors",
        datainputs=datainputs,
    )

    assert_response_success(resp)


@pytest.mark.parametrize(
    ("netcdf"), [(TESTDATA["test_vector_flow"]["netcdf"])],
)
@pytest.mark.parametrize(
    ("kwargs"),
    [
        (
            {
                "dest_file": "output.nc",
                "variable": "Flow_Direction",
            }
        ),
    ],
)
def test_wps_decompose_flow_vectors_netcdf(netcdf, kwargs):
    client = client_for(Service(processes=[DecomposeFlowVectors()]))
    datainputs = (
        "netcdf=@xlink:href={0};"
        "dest_file={dest_file};"
        "variable={variable};"
    ).format(netcdf, **kwargs)

    resp = client.get(
        service="wps",
        request="Execute",
        version="1.0.0",
        identifier="decompose_flow_vectors",
        datainputs=datainputs,
    )

    assert_response_success(resp)