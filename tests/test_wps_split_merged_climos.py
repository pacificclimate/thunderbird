import pytest

from pywps import Service
from pywps.tests import assert_response_success

from .common import client_for, TESTDATA
from thunderbird.processes.wps_split_merged_climos import SplitMergedClimos

test_gcm_360_climos = TESTDATA["test_local_nc"][1]
test_gcm_climos = TESTDATA["test_local_nc"][3]
test_tasmax_climos = TESTDATA["test_local_nc"][12]
test_hydromodel_gcm_climos = TESTDATA["test_local_nc"][14]


@pytest.mark.parametrize(
    ("netcdf"),
    [
        (test_gcm_360_climos),
        (test_gcm_climos),
        (test_tasmax_climos),
        (test_hydromodel_gcm_climos),
    ],
)
def test_single_file_local(netcdf):
    client = client_for(Service(processes=[SplitMergedClimos()]))
    datainputs = ("netcdf=@xlink:href={};").format(netcdf)

    resp = client.get(
        service="wps",
        request="Execute",
        version="1.0.0",
        identifier="split_merged_climos",
        datainputs=datainputs,
    )
    assert_response_success(resp)
