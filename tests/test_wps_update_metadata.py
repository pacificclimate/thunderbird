import pytest
import os
from pkg_resources import resource_filename, resource_listdir

from .utils import TESTDATA
from wps_tools.testing import run_wps_process, local_path, url_path
from thunderbird.processes.wps_update_metadata import UpdateMetadata

# limiting the test data to tiny_datasets
local_data = [
    local_path(nc) for nc in TESTDATA["test_local_nc"] if nc.startswith("tiny_")
]
opendap_data = [
    url_path(opendap, "opendap")
    for opendap in TESTDATA["test_opendaps"]
    if opendap.startswith("tiny_")
]

# updates yaml files
updates_yaml = [
    resource_filename("tests", "metadata-conversion/" + test_file)
    for test_file in resource_listdir("tests", "metadata-conversion")
]
# updates instruction strings
updates_str = [
    """
global:
    history: "today is a nice day"
"""
]


def build_params(netcdf, updates):
    if os.path.isfile(updates):
        return f"netcdf=@xlink:href={netcdf};updates_file={updates};"
    else:
        return f"netcdf=@xlink:href={netcdf};updates_string={updates};"


@pytest.mark.online
@pytest.mark.parametrize(
    ("netcdf"), opendap_data,
)
@pytest.mark.parametrize(
    ("updates"), updates_yaml,
)
def test_wps_update_metadata_opendap_yaml(netcdf, updates):
    run_wps_process(UpdateMetadata(), build_params(netcdf, updates))


@pytest.mark.online
@pytest.mark.parametrize(
    ("netcdf"), opendap_data,
)
@pytest.mark.parametrize(
    ("updates"), updates_str,
)
def test_wps_update_metadata_opendap_str(netcdf, updates):
    run_wps_process(UpdateMetadata(), build_params(netcdf, updates))


@pytest.mark.parametrize(
    ("netcdf"), local_data,
)
@pytest.mark.parametrize(
    ("updates"), updates_yaml,
)
def test_wps_update_metadata_netcdf_yaml(netcdf, updates):
    run_wps_process(UpdateMetadata(), build_params(netcdf, updates))


@pytest.mark.parametrize(
    ("netcdf"), local_data,
)
@pytest.mark.parametrize(
    ("updates"), updates_str,
)
def test_wps_update_metadata_netcdf_str(netcdf, updates):
    run_wps_process(UpdateMetadata(), build_params(netcdf, updates))
