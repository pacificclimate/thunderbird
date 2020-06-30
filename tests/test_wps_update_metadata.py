import pytest

from pywps import Service
from pywps.tests import assert_response_success

from .common import TESTDATA, run_wps_process
from thunderbird.processes.wps_update_metadata import UpdateMetadata


def build_params(netcdf, updates):
    return ("netcdf=@xlink:href={0};" "updates={1};").format(netcdf, updates)


@pytest.mark.online
@pytest.mark.parametrize(
    ("netcdf"), [(TESTDATA["test_opendap_seasonal"])],
)
@pytest.mark.parametrize(
    ("updates"), TESTDATA["test_yaml"],
)
def test_wps_update_metadata_opendap(netcdf, updates):
    params = build_params(netcdf, updates)
    run_wps_process(UpdateMetadata(), params)


@pytest.mark.parametrize(
    ("netcdf"), TESTDATA["test_local_nc"],
)
@pytest.mark.parametrize(
    ("updates"), TESTDATA["test_yaml"],
)
def test_wps_update_metadata_netcdf(netcdf, updates):
    params = build_params(netcdf, updates)
    run_wps_process(UpdateMetadata(), params)
