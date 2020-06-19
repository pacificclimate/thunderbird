import pytest

from pywps import Service
from pywps.tests import assert_response_success

from .common import client_for, TESTDATA
from thunderbird.processes.wps_generate_climos import GenerateClimos


def run_wps_generate_climos(netcdf, datainputs):
    client = client_for(Service(processes=[GenerateClimos()]))

    resp = client.get(
        service="wps",
        request="Execute",
        version="1.0.0",
        identifier="generate_climos",
        datainputs=datainputs,
    )
    assert_response_success(resp)


@pytest.mark.online
@pytest.mark.parametrize(
    ("netcdf"), [(TESTDATA["test_opendap"])],
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
    datainputs = (
        "netcdf=@xlink:href={0};"
        "operation={operation};"
        "climo={climo};"
        "resolutions={resolutions};"
        "convert_longitudes={convert_longitudes};"
        "split_vars={split_vars};"
        "split_intervals={split_intervals};"
        "dry_run={dry_run};"
    ).format(netcdf, **kwargs)

    run_wps_generate_climos(netcdf, datainputs)


# running generate_climos on climo files is againt the purpose of the program
local_test_data = [
    nc for nc in TESTDATA["test_local_nc"] if not nc.endswith("_climos.nc")
]


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
    datainputs = (
        "netcdf=@xlink:href={0};"
        "operation={operation};"
        "climo={climo};"
        "resolutions={resolutions};"
        "convert_longitudes={convert_longitudes};"
        "split_vars={split_vars};"
        "split_intervals={split_intervals};"
        "dry_run={dry_run};"
    ).format(netcdf, **kwargs)

    run_wps_generate_climos(netcdf, datainputs)


@pytest.mark.parametrize(
    ("netcdf"), local_test_data,
)
@pytest.mark.parametrize(
    ("kwargs"), [({"operation": "mean", "dry_run": "False",}),],
)
def test_missing_arguments(netcdf, kwargs):
    client = client_for(Service(processes=[GenerateClimos()]))
    datainputs = (
        "netcdf=@xlink:href={0};" "operation={operation};" "dry_run={dry_run};"
    ).format(netcdf, **kwargs)

    run_wps_generate_climos(netcdf, datainputs)
