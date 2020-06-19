import pytest

from pywps import Service
from pywps.tests import assert_response_success

from netCDF4 import Dataset
from .common import client_for, TESTDATA
from thunderbird.processes.wps_decompose_flow_vectors import DecomposeFlowVectors
from pywps.app.exceptions import ProcessError
import owslib.wps
import pkg_resources
import os
import re

flow_vectors_opendap = "http://docker-dev03.pcic.uvic.ca:8083/twitcher/ows/proxy/thredds/dodsC/datasets/TestData/sample_flow_parameters.nc"
flow_vectors_nc = "file:///{}".format(
    pkg_resources.resource_filename(__name__, "data/sample_flow_parameters.nc")
)


@pytest.mark.online
@pytest.mark.parametrize(
    ("opendap"), [flow_vectors_opendap],
)
@pytest.mark.parametrize(
    ("kwargs"), [({"dest_file": "output.nc", "variable": "Flow_Direction",}),],
)
def test_wps_decompose_flow_vectors_opendap(opendap, kwargs):
    client = client_for(Service(processes=[DecomposeFlowVectors()]))
    datainputs = (
        "opendap=@xlink:href={0};" "dest_file={dest_file};" "variable={variable};"
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
    ("netcdf"), [flow_vectors_nc],
)
@pytest.mark.parametrize(
    ("kwargs"), [({"dest_file": "output.nc", "variable": "Flow_Direction",}),],
)
def test_wps_decompose_flow_vectors_netcdf(netcdf, kwargs):
    client = client_for(Service(processes=[DecomposeFlowVectors()]))
    datainputs = (
        "netcdf=@xlink:href={0};" "dest_file={dest_file};" "variable={variable};"
    ).format(netcdf, **kwargs)

    resp = client.get(
        service="wps",
        request="Execute",
        version="1.0.0",
        identifier="decompose_flow_vectors",
        datainputs=datainputs,
    )

    assert_response_success(resp)


@pytest.mark.parametrize(
    ("netcdf"), TESTDATA["test_local_nc"],
)
def test_input_check(netcdf):
    source_file = re.sub("file:///", "", netcdf)
    source = Dataset(source_file, "r", format="NETCDF4")

    dfv = DecomposeFlowVectors()
    try:
        dfv.source_check(source)
        assertion = False
    except ProcessError:
        assertion = True

    assert assertion
