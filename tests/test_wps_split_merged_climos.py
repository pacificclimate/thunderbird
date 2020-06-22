import pytest

from pywps import Service
from pywps.tests import assert_response_success

from .common import client_for, TESTDATA
from thunderbird.processes.wps_split_merged_climos import SplitMergedClimos

gcm_360_climos_local = TESTDATA["test_local_gcm_360_climos_nc"]
gcm_climos_local = TESTDATA["test_local_gcm_climos_nc"]
tasmax_climos_local = TESTDATA["test_local_tasmax_climos_nc"]
gcm_360_climos_opendap = TESTDATA["test_opendap_gcm_360_climos_nc"]
gcm_climos_opendap = TESTDATA["test_opendap_gcm_climos_nc"]
tasmax_climos_opendap = TESTDATA["test_opendap_tasmax_climos_nc"]

client = client_for(Service(processes=[SplitMergedClimos()]))


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
    datainputs = ("netcdf=@xlink:href={};").format(netcdf)
    check_success(datainputs)


def run_multiple_files(netcdf):
    datainputs = ""
    for i in range(len(netcdf)):
        datainputs += "netcdf=@xlink:href={};".format(netcdf[i])
    check_success(datainputs)


@pytest.mark.parametrize(
    ("netcdf"), [(gcm_360_climos_local), (gcm_climos_local), (tasmax_climos_local),],
)
def test_single_file_local(netcdf):
    run_single_file(netcdf)


@pytest.mark.parametrize(
    ("netcdf"),
    [
        (gcm_360_climos_local, gcm_climos_local),
        (gcm_climos_local, tasmax_climos_local),
        (gcm_360_climos_local, gcm_climos_local, tasmax_climos_local),
    ],
)
def test_multiple_files_local(netcdf):
    run_multiple_files(netcdf)


@pytest.mark.online
@pytest.mark.parametrize(
    ("netcdf"),
    [(gcm_360_climos_opendap), (gcm_climos_opendap), (tasmax_climos_opendap),],
)
def test_single_file_opendap(netcdf):
    run_single_file(netcdf)


@pytest.mark.online
@pytest.mark.parametrize(
    ("netcdf"),
    [
        (gcm_360_climos_opendap, gcm_climos_opendap),
        (gcm_climos_opendap, tasmax_climos_opendap),
        (gcm_360_climos_opendap, gcm_climos_opendap, tasmax_climos_opendap),
    ],
)
def test_multiple_files_opendap(netcdf):
    run_multiple_files(netcdf)


@pytest.mark.online
@pytest.mark.parametrize(
    ("netcdf"),
    [
        (gcm_360_climos_local, gcm_climos_opendap),
        (gcm_climos_local, tasmax_climos_opendap),
        (gcm_360_climos_opendap, gcm_climos_local, tasmax_climos_local),
    ],
)
def test_multiple_files_mixed(netcdf):
    run_multiple_files(netcdf)
