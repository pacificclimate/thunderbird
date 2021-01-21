import pytest


from .testdata import TESTDATA, process_err_test
from wps_tools.testing import run_wps_process, local_path, url_path
from thunderbird.processes.wps_generate_climos import GenerateClimos

# limiting test_data to non-climo tiny datasets
local_test_data = [
    local_path(nc)
    for nc in TESTDATA["test_local_nc"]
    if nc.startswith("tiny_") and not nc.endswith("_climos.nc") and "_gcm" not in nc
]
# NetCDFs with flow_vectors not adequate for generate_climos
# refer to https://github.com/pacificclimate/climate-explorer-data-prep#generate_climos-generate-climatological-means
opendap_data = [
    url_path(opendap, "opendap")
    for opendap in TESTDATA["test_opendaps"]
    if not (
        opendap.endswith("_climos.nc")
        or opendap.endswith("sample_flow_parameters.nc")
        or opendap.endswith("19500107.nc")
    )
]


def build_netcdf(netcdf):
    if isinstance(netcdf, str):  # Single input file
        return f"netcdf=@xlink:href={netcdf};"
    else:
        nc_input = ""
        for nc in netcdf:
            nc_input += f"netcdf=@xlink:href={nc};"
        return nc_input


def build_resolutions(resolutions):
    if isinstance(resolutions, str):  # Single resolution
        return f"resolutions={resolutions};"
    else:
        res_input = ""
        for res in resolutions:
            res_input += f"resolutions={res};"
        return res_input


def build_params(netcdf, kwargs):
    return (
        "{nc_input}"
        "{res_input}"
        "operation={operation};"
        "climo={climo};"
        "convert_longitudes={convert_longitudes};"
        "split_vars={split_vars};"
        "split_intervals={split_intervals};"
        "dry_run={dry_run};"
    ).format(
        nc_input=build_netcdf(netcdf),
        res_input=build_resolutions(kwargs["resolutions"]),
        **kwargs,
    )


@pytest.mark.slow
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
                "resolutions": ["seasonal", "yearly"],
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
                "resolutions": "all",
                "convert_longitudes": "False",
                "split_vars": "False",
                "split_intervals": "False",
                "dry_run": "True",
            }
        ),
    ],
)
def test_wps_gen_climos_opendap_single(netcdf, kwargs):
    params = build_params(netcdf, kwargs)
    run_wps_process(GenerateClimos(), params)


@pytest.mark.parametrize(
    ("netcdf"),
    [(local_path("tiny_gcm_360_day_cal.nc")), (local_path("tiny_hydromodel_gcm.nc")),],
)
@pytest.mark.parametrize(
    ("kwargs"),
    [
        (
            {
                "operation": "std",
                "climo": "6190",
                "resolutions": ["seasonal", "yearly"],
                "convert_longitudes": "True",
                "split_vars": "True",
                "split_intervals": "True",
                "dry_run": "False",
            }
        ),
    ],
)
def test_wps_gen_climos_input_check(netcdf, kwargs):
    params = build_params(netcdf, kwargs)
    process_err_test(GenerateClimos, params)


@pytest.mark.slow
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
                "resolutions": ["monthly", "seasonal", "yearly"],
                "convert_longitudes": "True",
                "split_vars": "True",
                "split_intervals": "True",
                "dry_run": "False",
            }
        ),
        (
            {
                "operation": "std",
                "climo": "6190",
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


@pytest.mark.slow
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
                "resolutions": ["monthly", "seasonal", "yearly"],
                "convert_longitudes": "True",
                "split_vars": "True",
                "split_intervals": "True",
                "dry_run": "False",
            }
        ),
    ],
)
def test_wps_gen_climos_local_nc(netcdf, kwargs):
    params = build_params(netcdf, kwargs)
    run_wps_process(GenerateClimos(), params)


@pytest.mark.slow
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
