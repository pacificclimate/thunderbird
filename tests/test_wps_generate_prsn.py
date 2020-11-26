import pytest
import re


from .testdata import TESTDATA
from wps_tools.testing import run_wps_process, local_path, url_path
from thunderbird.processes.wps_generate_prsn import GeneratePrsn

local_nc_inputs = {
    nc.split("_")[0]: local_path(nc)
    for nc in TESTDATA["test_local_nc"]
    if nc.startswith("pr_") or nc.startswith("tasmin_") or nc.startswith("tasmax_")
}

local_tiny_nc_inputs = {
    re.sub(".nc", "", nc.split("_")[-1]): local_path(nc)
    for nc in TESTDATA["test_local_nc"]
    if nc.startswith("tiny_daily")
}

opendap_inputs = {
    opendap.split("_")[0]: url_path(opendap, "opendap")
    for opendap in TESTDATA["test_opendaps"]
    if opendap.startswith("pr_")
    or opendap.startswith("tasmin_")
    or opendap.startswith("tasmax_")
}


def build_params(netcdfs, dry_run, chunk_size=None, output_file=None):
    output = (
        f"prec=@xlink:href={netcdfs['pr']};"
        f"tasmin=@xlink:href={netcdfs['tasmin']};"
        f"tasmax=@xlink:href={netcdfs['tasmax']};"
        f"dry_run={dry_run};"
    )

    if chunk_size and output_file:
        output += f"chunk_size={chunk_size};" f"output_file={output_file};"

    return output


@pytest.mark.parametrize(
    ("netcdfs"), [local_nc_inputs, local_tiny_nc_inputs,],
)
@pytest.mark.parametrize(
    ("dry_run"), [("False")],
)
def test_default_local(netcdfs, dry_run):
    params = build_params(netcdfs, dry_run)
    run_wps_process(GeneratePrsn(), params)


@pytest.mark.parametrize(
    ("netcdfs"), [local_nc_inputs, local_tiny_nc_inputs,],
)
@pytest.mark.parametrize(
    ("chunk_size", "dry_run", "output_file"), [("50", "True", "prsn_test_local.nc"),],
)
def test_run_local(netcdfs, chunk_size, dry_run, output_file):
    params = build_params(netcdfs, dry_run, chunk_size, output_file)
    run_wps_process(GeneratePrsn(), params)


@pytest.mark.slow
@pytest.mark.online
@pytest.mark.parametrize(
    ("opendaps"), [opendap_inputs],
)
@pytest.mark.parametrize(
    ("dry_run"), [("False")],
)
def test_default_opendap(opendaps, dry_run):
    params = build_params(opendaps, dry_run)
    run_wps_process(GeneratePrsn(), params)


@pytest.mark.slow
@pytest.mark.online
@pytest.mark.parametrize(
    ("opendaps"), [opendap_inputs],
)
@pytest.mark.parametrize(
    ("chunk_size", "dry_run", "output_file"),
    [("50", "False", "prsn_test_opendap.nc"),],
)
def test_run_opendap(opendaps, chunk_size, dry_run, output_file):
    params = build_params(opendaps, dry_run, chunk_size, output_file)
    run_wps_process(GeneratePrsn(), params)


@pytest.mark.slow
@pytest.mark.online
# exclude tiny_datasets to mix within "day_BCCAQv2%2BANUSPLIN300_NorESM1-M_historical%2Brcp26_r1i1p1_19500101-19500107.nc" datasets
@pytest.mark.parametrize(
    ("netcdfs"),
    [
        (
            {
                "pr": local_nc_inputs["pr"],
                "tasmin": opendap_inputs["tasmin"],
                "tasmax": opendap_inputs["tasmax"],
            }
        ),
        (
            {
                "pr": opendap_inputs["pr"],
                "tasmin": local_nc_inputs["tasmin"],
                "tasmax": local_nc_inputs["tasmax"],
            }
        ),
    ],
)
@pytest.mark.parametrize(
    ("chunk_size", "dry_run", "output_file"),
    [
        ("100", "True", "prsn_test_mixed1.nc",),
        ("100", "False", "prsn_test_mixed2.nc",),
    ],
)
def test_run_mixed(netcdfs, chunk_size, dry_run, output_file):
    params = build_params(netcdfs, dry_run, chunk_size, output_file)
    run_wps_process(GeneratePrsn(), params)
