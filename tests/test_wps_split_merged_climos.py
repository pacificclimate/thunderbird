import pytest

from pywps import Service
from pywps.tests import assert_response_success

from .common import client_for, TESTDATA, local_path, opendap_path
from thunderbird.processes.wps_split_merged_climos import SplitMergedClimos

# limiting test_data to climo files
climo_local_files = [
    local_path(nc) for nc in TESTDATA["test_local_nc"] if nc.endswith("_climos.nc")
]
climo_opendaps = [
    opendap_path(opendap)
    for opendap in TESTDATA["test_opendaps"]
    if opendap.endswith("_climos.nc")
]

client = client_for(Service(processes=[SplitMergedClimos()]))


def build_netcdf_combinations(climo_files):
    """
    This function takes a list of climo_files and returns a list of
    combinations of climo_files. The purpose of this it is to make
    test cases for wps_split_merged_climos to handle multiple inputs.
    For example if [climo1, climo2, climo3] is given as an input, it
    returns the following output: 
    [
        (climo1, climo2),
        (climo1, climo3),
        (climo2, climo3),
        (climo1, climo2, climo3) <--- This is the worst case scenario
    ]
    """
    netcdf_sets = []

    for first_idx, first_component in enumerate(climo_files):
        second_idx = first_idx + 1
        while second_idx < len(climo_files):
            second_component = climo_files[second_idx]
            netcdf_sets.append((first_component, second_component))
            second_idx += 1

    netcdf_sets.append(tuple(climo_files))
    return netcdf_sets


def check_success(datainputs):
    resp = client.get(
        service="wps",
        request="Execute",
        version="1.0.0",
        identifier="split_merged_climos",
        datainputs=datainputs,
    )
    assert_response_success(resp)


def run_single_file(netcdf):
    datainputs = f"netcdf=@xlink:href={netcdf};"
    check_success(datainputs)


def run_multiple_files(netcdfs):
    datainputs = ""
    for netcdf in netcdfs:
        datainputs += f"netcdf=@xlink:href={netcdf};"
    check_success(datainputs)


@pytest.mark.parametrize(
    "netcdf", climo_local_files,
)
def test_single_file_local(netcdf):
    run_single_file(netcdf)


@pytest.mark.parametrize(
    "netcdfs", build_netcdf_combinations(climo_local_files),
)
def test_multiple_files_local(netcdfs):
    run_multiple_files(netcdfs)


@pytest.mark.online
@pytest.mark.parametrize(
    "netcdf", climo_opendaps,
)
def test_single_file_opendap(netcdf):
    run_single_file(netcdf)


@pytest.mark.online
@pytest.mark.parametrize(("netcdfs"), build_netcdf_combinations(climo_opendaps))
def test_multiple_files_opendap(netcdfs):
    run_multiple_files(netcdfs)


@pytest.mark.online
@pytest.mark.parametrize(
    ("netcdfs"), build_netcdf_combinations(climo_local_files + climo_opendaps),
)
def test_multiple_files_mixed(netcdfs):
    run_multiple_files(netcdfs)
