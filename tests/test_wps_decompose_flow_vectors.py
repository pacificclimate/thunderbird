import pytest


from .testdata import TESTDATA
from wps_tools.testing import run_wps_process, local_path, url_path
from thunderbird.processes.wps_decompose_flow_vectors import DecomposeFlowVectors


import owslib.wps
import pkg_resources
import os

# limiting test_data to "sample_flow_parameters.nc"
flow_vectors_opendap = [
    url_path(opendap, "opendap")
    for opendap in TESTDATA["test_opendaps"]
    if opendap.endswith("sample_flow_parameters.nc")
]
flow_vectors_nc = [
    local_path(nc)
    for nc in TESTDATA["test_local_nc"]
    if nc.endswith("sample_flow_parameters.nc")
]
# tiny_datasets do not have flow vectors
non_flow_vectors_nc = [
    local_path(nc) for nc in TESTDATA["test_local_nc"] if nc.startswith("tiny_")
]


def build_params(netcdf, kwargs):
    return (
        "netcdf=@xlink:href={0};" "dest_file={dest_file};" "variable={variable};"
    ).format(netcdf, **kwargs)


@pytest.mark.slow
@pytest.mark.online
@pytest.mark.parametrize(
    ("opendap"), flow_vectors_opendap,
)
@pytest.mark.parametrize(
    ("kwargs"), [({"dest_file": "output.nc", "variable": "Flow_Direction",}),],
)
def test_wps_decompose_flow_vectors_opendap(opendap, kwargs):
    params = build_params(opendap, kwargs)
    run_wps_process(DecomposeFlowVectors(), params)


@pytest.mark.parametrize(
    ("netcdf"), flow_vectors_nc,
)
@pytest.mark.parametrize(
    ("kwargs"), [({"dest_file": "output.nc", "variable": "Flow_Direction",}),],
)
def test_wps_decompose_flow_vectors_netcdf(netcdf, kwargs):
    params = build_params(netcdf, kwargs)
    run_wps_process(DecomposeFlowVectors(), params)


@pytest.mark.parametrize(
    ("netcdf"), non_flow_vectors_nc,
)
@pytest.mark.parametrize(
    ("kwargs"), [({"dest_file": "output.nc", "variable": "Flow_Direction",}),],
)
def test_source_check(netcdf, kwargs):
    params = build_params(netcdf, kwargs)

    with pytest.raises(Exception):
        run_wps_process(DecomposeFlowVectors(), params)


@pytest.mark.parametrize(
    ("netcdf"), [(flow_vectors_nc)],
)
@pytest.mark.parametrize(
    ("kwargs"),
    [
        ({"dest_file": "output.nc", "variable": "not a variable",}),
        ({"dest_file": "output.nc", "variable": "crs",}),
        ({"dest_file": "output.nc", "variable": "lat",}),
        ({"dest_file": "output.nc", "variable": "lon",}),
        ({"dest_file": "output.nc", "variable": "diffusion",}),
        ({"dest_file": "output.nc", "variable": "Flow_Distance",}),
        ({"dest_file": "output.nc", "variable": "Basin_ID",}),
        ({"dest_file": "output.nc", "variable": "velocity",}),
        ({"dest_file": "output.nc", "variable": "flow_direction",}),
    ],
)
def test_variable_check(netcdf, kwargs):
    params = build_params(netcdf, kwargs)

    with pytest.raises(Exception):
        run_wps_process(DecomposeFlowVectors(), params)
