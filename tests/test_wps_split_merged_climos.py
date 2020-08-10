import pytest

from pywps import Service
from pywps.tests import assert_response_success

from .testdata import TESTDATA
from wps_tools.testing import run_wps_process, local_path, opendap_path
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


def run_single_file(netcdf):
    datainputs = f"netcdf=@xlink:href={netcdf};"
    run_wps_process(SplitMergedClimos(), datainputs)


def run_multiple_files(netcdfs):
    datainputs = ""
    for netcdf in netcdfs:
        datainputs += f"netcdf=@xlink:href={netcdf};"
    run_wps_process(SplitMergedClimos(), datainputs)


@pytest.mark.parametrize(
    "netcdf", climo_local_files,
)
def test_single_file_local(netcdf):
    run_single_file(netcdf)


@pytest.mark.parametrize(
    "netcdfs",
    [
        (climo_local_files[0], climo_local_files[1]),
        (climo_local_files[0], climo_local_files[1], climo_local_files[2]),
    ],
)
def test_multiple_files_local(netcdfs):
    run_multiple_files(netcdfs)


@pytest.mark.online
@pytest.mark.parametrize(
    "netcdf", climo_opendaps,
)
def test_single_file_opendap(netcdf):
    run_single_file(netcdf)


@pytest.mark.slow
@pytest.mark.online
@pytest.mark.parametrize(
    "netcdfs",
    [
        (climo_opendaps[0], climo_opendaps[1]),
        (climo_opendaps[0], climo_opendaps[1], climo_opendaps[2]),
    ],
)
def test_multiple_files_opendap(netcdfs):
    run_multiple_files(netcdfs)


@pytest.mark.slow
@pytest.mark.online
@pytest.mark.parametrize(
    ("netcdfs"),
    [
        (climo_local_files[0], climo_opendaps[1]),
        (climo_opendaps[0], climo_local_files[1], climo_opendaps[2]),
    ],
)
def test_multiple_files_mixed(netcdfs):
    run_multiple_files(netcdfs)
