import pytest
import re

from pywps import Service
from pywps.tests import assert_response_success

from .common import TESTDATA, run_wps_process
from thunderbird.processes.wps_generate_climos import GenerateClimos

# running generate_climos on climo files is againt the purpose of the program
local_test_data = [
    nc
    for nc in TESTDATA["test_local_nc"]
    if not nc.endswith("_climos.nc") and re.search("\w*/tiny_\w+.nc$", nc)
]
opendap_data = [od for od in TESTDATA["test_opendaps"] if not od.endswith("_climos.nc")]


def build_params(netcdf, kwargs):
    return (
        "netcdf=@xlink:href={0};"
        "operation={operation};"
        "climo={climo};"
        "resolutions={resolutions};"
        "convert_longitudes={convert_longitudes};"
        "split_vars={split_vars};"
        "split_intervals={split_intervals};"
        "dry_run={dry_run};"
    ).format(netcdf, **kwargs)


@pytest.mark.online
@pytest.mark.parametrize(
    ("netcdf"), opendap_data,
)
@pytest.mark.parametrize(
    ("kwargs"),
    [
        (
            {
                "operation": "mean",
                "climo": "6190",
                "resolutions": "all",
                "convert_longitudes": "True",
                "split_vars": "True",
                "split_intervals": "True",
                "dry_run": "False",
            }
        ),
        (
            {
                "operation": "std",
                "climo": "7100",
                "resolutions": "monthly",
                "convert_longitudes": "False",
                "split_vars": "False",
                "split_intervals": "False",
                "dry_run": "True",
            }
        ),
    ],
)
def test_wps_gen_climos_opendap(netcdf, kwargs):
    params = build_params(netcdf, kwargs)
    run_wps_process(GenerateClimos(), params)


@pytest.mark.parametrize(
    ("netcdf"), local_test_data,
)
@pytest.mark.parametrize(
    ("kwargs"),
    [
        (
            {
                "operation": "mean",
                "climo": "6190",
                "resolutions": "all",
                "convert_longitudes": "True",
                "split_vars": "True",
                "split_intervals": "True",
                "dry_run": "False",
            }
        ),
        (
            {
                "operation": "std",
                "climo": "7100",
                "resolutions": "monthly",
                "convert_longitudes": "False",
                "split_vars": "False",
                "split_intervals": "False",
                "dry_run": "True",
            }
        ),
    ],
)
def test_wps_gen_climos_local_nc(netcdf, kwargs):
    params = build_params(netcdf, kwargs)
    run_wps_process(GenerateClimos(), params)


@pytest.mark.parametrize(
    ("netcdf"), local_test_data,
)
@pytest.mark.parametrize(
    ("kwargs"), [({"operation": "mean", "dry_run": "False",}),],
)
def test_missing_arguments(netcdf, kwargs):
    params = (
        "netcdf=@xlink:href={0};" "operation={operation};" "dry_run={dry_run};"
    ).format(netcdf, **kwargs)
    run_wps_process(GenerateClimos(), params)
