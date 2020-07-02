import pytest

from pywps import Service
from pywps.tests import assert_response_success

from .common import client_for, TESTDATA
from thunderbird.processes.wps_split_merged_climos import SplitMergedClimos

split_merged_climos_local = [
    nc for nc in TESTDATA["test_local_nc"] if nc.endswith("_climos.nc")
]
split_merged_climos_opendap = [
    od for od in TESTDATA["test_opendaps"] if od.endswith("_climos.nc")
]

client = client_for(Service(processes=[SplitMergedClimos()]))


def build_netcdf_sets(climo_files):
    netcdf_sets = []

    i = 0
    while i < len(climo_files):
        j = i + 1
        while j < len(climo_files):
            netcdf_sets.append((climo_files[i], climo_files[j]))
            j += 1
        i += 1

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
    ("netcdf"), split_merged_climos_local,
)
def test_single_file_local(netcdf):
    run_single_file(netcdf)


@pytest.mark.parametrize(
    ("netcdfs"), build_netcdf_sets(split_merged_climos_local),
)
def test_multiple_files_local(netcdfs):
    run_multiple_files(netcdfs)


@pytest.mark.online
@pytest.mark.parametrize(
    ("netcdf"), split_merged_climos_opendap,
)
def test_single_file_opendap(netcdf):
    run_single_file(netcdf)


@pytest.mark.online
@pytest.mark.parametrize(("netcdfs"), build_netcdf_sets(split_merged_climos_opendap))
def test_multiple_files_opendap(netcdfs):
    run_multiple_files(netcdfs)


@pytest.mark.online
@pytest.mark.parametrize(
    ("netcdfs"),
    build_netcdf_sets(split_merged_climos_local + split_merged_climos_opendap),
)
def test_multiple_files_mixed(netcdfs):
    run_multiple_files(netcdfs)
