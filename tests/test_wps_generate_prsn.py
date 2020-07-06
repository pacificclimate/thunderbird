import pytest
import re

from pywps import Service
from pywps.tests import assert_response_success

from .common import TESTDATA, run_wps_process
from thunderbird.processes.wps_generate_prsn import GeneratePrsn

local_test_files = TESTDATA["test_local_nc"]
# pr, tasmin and tasmax files to make vaild sets of test_data
local_pr_files = [f for f in local_test_files if "pr" in f]
local_tasmin_files = [f for f in local_test_files if "tasmin" in f]
local_tasmax_files = [f for f in local_test_files if "tasmax" in f]

# creating sets of test_data with the matching files
netcdf_sets = [
    (pr, tasmin, tasmax)
    for pr in local_pr_files
    for tasmin in local_tasmin_files
    for tasmax in local_tasmax_files
    if re.sub("pr", "", pr) == re.sub("tasmin", "", tasmin)
    and re.sub("pr", "", pr) == re.sub("tasmax", "", tasmax)
]

opendap_set = ["", "", ""]
for od in TESTDATA["test_opendaps"]:
    if re.search("\S*/pr_\S+.nc$", od):
        opendap_set[0] = od
    elif re.search("\S*/tasmin_\S+.nc$", od):
        opendap_set[1] = od
    elif re.search("\S*/tasmax_\S+.nc$", od):
        opendap_set[2] = od

opendap_set = [tuple(opendap_set)]


def build_params(netcdfs, dry_run, chunk_size=None, output_file=None):
    prec, tasmin, tasmax = netcdfs
    output = (
        f"prec=@xlink:href={prec};"
        f"tasmin=@xlink:href={tasmin};"
        f"tasmax=@xlink:href={tasmax};"
        f"dry_run={dry_run};"
    )

    if chunk_size and output_file:
        output += f"chunk_size={chunk_size};" f"output_file={output_file};"

    return output


@pytest.mark.parametrize(
    ("netcdfs"), netcdf_sets,
)
@pytest.mark.parametrize(
    ("dry_run"), [("False")],
)
def test_default_local(netcdfs, dry_run):
    params = build_params(netcdfs, dry_run)
    run_wps_process(GeneratePrsn(), params)


@pytest.mark.parametrize(
    ("netcdfs"), netcdf_sets,
)
@pytest.mark.parametrize(
    ("chunk_size", "dry_run", "output_file"), [("50", "True", "prsn_test_local.nc"),],
)
def test_run_local(netcdfs, chunk_size, dry_run, output_file):
    params = build_params(netcdfs, dry_run, chunk_size, output_file)
    run_wps_process(GeneratePrsn(), params)


@pytest.mark.online
@pytest.mark.parametrize(
    ("opendaps"), opendap_set,
)
@pytest.mark.parametrize(
    ("dry_run"), [("False")],
)
def test_default_opendap(opendaps, dry_run):
    params = build_params(opendaps, dry_run)
    run_wps_process(GeneratePrsn(), params)


@pytest.mark.online
@pytest.mark.parametrize(
    ("opendaps"), opendap_set,
)
@pytest.mark.parametrize(
    ("chunk_size", "dry_run", "output_file"),
    [("50", "False", "prsn_test_opendap.nc"),],
)
def test_run_opendap(opendaps, chunk_size, dry_run, output_file):
    params = build_params(opendaps, dry_run, chunk_size, output_file)
    run_wps_process(GeneratePrsn(), params)


@pytest.mark.online
# exclude tiny_datasets to mix within "day_BCCAQv2%2BANUSPLIN300_NorESM1-M_historical%2Brcp26_r1i1p1_19500101-19500107.nc" datasets
@pytest.mark.parametrize(
    ("netcdfs"),
    [nc_set for nc_set in netcdf_sets if not re.search("\S*/tiny_\S+.nc$", nc_set[0])],
)
@pytest.mark.parametrize(
    ("opendaps"), opendap_set,
)
@pytest.mark.parametrize(
    ("chunk_size", "dry_run", "output_file"),
    [
        ("100", "True", "prsn_test_mixed1.nc",),
        ("100", "False", "prsn_test_mixed2.nc",),
    ],
)
def test_run_mixed(netcdfs, opendaps, chunk_size, dry_run, output_file):
    mixed1 = (netcdfs[0], opendaps[1], opendaps[2])
    mixed2 = (opendaps[0], netcdfs[1], netcdfs[2])
    params1 = build_params(mixed1, dry_run, chunk_size, output_file)
    params2 = build_params(mixed2, dry_run, chunk_size, output_file)

    run_wps_process(GeneratePrsn(), params1)
    run_wps_process(GeneratePrsn(), params2)
