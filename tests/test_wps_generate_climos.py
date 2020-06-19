import pytest

from pywps import Service
from pywps.tests import assert_response_success

from .common import client_for, TESTDATA
from thunderbird.processes.wps_generate_climos import GenerateClimos


def run_wps_generate_climos(netcdf, kwargs):
    client = client_for(Service(processes=[GenerateClimos()]))
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
    run_wps_generate_climos(netcdf, kwargs)

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
    run_wps_generate_climos(netcdf, kwargs)


@pytest.mark.parametrize(
    ("resolutions", "expected"),
    [
        (["all"], ["yearly", "seasonal", "monthly"]),
        (["all", "yearly"], ["yearly", "seasonal", "monthly"]),
        (["yearly"], ["yearly"]),
        (["monthly", "seasonal"], ["seasonal", "monthly"]),
    ],
)
def test_format_resolutions(resolutions, expected):
    gc = GenerateClimos()
    output = gc.format_resolutions(resolutions)
    print(output)
    assert len(output) == len(expected)
    for resolution in output:
        assert resolution in expected


@pytest.mark.parametrize(
    ("climo", "expected"),
    [
        (["all"], ["6190", "7100", "8100", "2020", "2050", "2080"]),
        (["all", "historical"], ["6190", "7100", "8100", "2020", "2050", "2080"],),
        (["all", "futures"], ["6190", "7100", "8100", "2020", "2050", "2080"],),
        (["futures"], ["2020", "2050", "2080"]),
        (["futures", "6190"], ["2020", "2050", "2080", "6190"]),
        (["historical", "2050"], ["6190", "7100", "8100", "2050"]),
        (
            ["historical", "futures", "6190", "2080"],
            ["6190", "7100", "8100", "2020", "2050", "2080"],
        ),
    ],
)
def test_format_climo(climo, expected):
    gc = GenerateClimos()
    output = gc.format_climo(climo)
    assert len(output) == len(expected)
    for climo in output:
        assert climo in expected
