import pytest

from pywps import Service
from pywps.tests import assert_response_success

from netCDF4 import Dataset
from .common import client_for, TESTDATA, run_wps_process
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


def build_params(netcdf, kwargs):
    return (
        "netcdf=@xlink:href={0};" "dest_file={dest_file};" "variable={variable};"
    ).format(netcdf, **kwargs)


@pytest.mark.online
@pytest.mark.parametrize(
    ("opendap"), [flow_vectors_opendap],
)
@pytest.mark.parametrize(
    ("kwargs"), [({"dest_file": "output.nc", "variable": "Flow_Direction",}),],
)
def test_wps_decompose_flow_vectors_opendap(opendap, kwargs):
    params = build_params(opendap, kwargs)
    run_wps_process(DecomposeFlowVectors(), params)


@pytest.mark.parametrize(
    ("netcdf"), [flow_vectors_nc],
)
@pytest.mark.parametrize(
    ("kwargs"), [({"dest_file": "output.nc", "variable": "Flow_Direction",}),],
)
def test_wps_decompose_flow_vectors_netcdf(netcdf, kwargs):
    params = build_params(netcdf, kwargs)
    run_wps_process(DecomposeFlowVectors(), params)

@pytest.mark.parametrize(
    ("netcdf"), TESTDATA["test_local_nc"],
)
@pytest.mark.parametrize(
    ("kwargs"), [({"dest_file": "output.nc", "variable": "Flow_Direction",}),],
)
def test_source_check(netcdf, kwargs):
    params = build_params(netcdf, kwargs)

    with pytest.raises(ProcessError) as exc:
        run_wps_process(DecomposeFlowVectors(), params)
    
    assert exc.value