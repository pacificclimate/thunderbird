import pytest
import re

from pywps import Service
from pywps.tests import assert_response_success

from .common import TESTDATA, run_wps_process
from thunderbird.processes.wps_generate_prsn import GeneratePrsn

local_test_files = TESTDATA["test_local_nc"]
local_pr_files = [f for f in local_test_files if "pr" in f]
local_tasmin_files = [f for f in local_test_files if "tasmin" in f]
local_tasmax_files = [f for f in local_test_files if "tasmax" in f]

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


def build_params(netcdfs, kwargs):
    # Not using default values
    if "chunk_size" in kwargs.keys() and "output_file" in kwargs.keys():
        return (
            "prec=@xlink:href={0};"
            "tasmin=@xlink:href={1};"
            "tasmax=@xlink:href={2};"
            "dry_run={dry_run};"
            "chunk_size={chunk_size};"
            "output_file={output_file};"
        ).format(netcdfs[0], netcdfs[1], netcdfs[2], **kwargs)
    # Using default values
    else:
        return (
            "prec=@xlink:href={0};"
            "tasmin=@xlink:href={1};"
            "tasmax=@xlink:href={2};"
            "dry_run={dry_run};"
        ).format(netcdfs[0], netcdfs[1], netcdfs[2], **kwargs)


@pytest.mark.parametrize(
    ("netcdfs"), netcdf_sets,
)
@pytest.mark.parametrize(
    ("kwargs"), [({"dry_run": "False",}),],
)
def test_default_local(netcdfs, kwargs):
    params = build_params(netcdfs, kwargs)
    run_wps_process(GeneratePrsn(), params)


@pytest.mark.parametrize(
    ("netcdfs"), netcdf_sets,
)
@pytest.mark.parametrize(
    ("kwargs"),
    [({"chunk_size": "50", "dry_run": "True", "output_file": "prsn_test_local.nc",}),],
)
def test_run_local(netcdfs, kwargs):
    params = build_params(netcdfs, kwargs)
    run_wps_process(GeneratePrsn(), params)


@pytest.mark.online
@pytest.mark.parametrize(
    ("opendaps"), opendap_set,
)
@pytest.mark.parametrize(
    ("kwargs"), [({"dry_run": "False",}),],
)
def test_default_opendap(opendaps, kwargs):
    params = build_params(opendaps, kwargs)
    run_wps_process(GeneratePrsn(), params)


@pytest.mark.online
@pytest.mark.parametrize(
    ("opendaps"), opendap_set,
)
@pytest.mark.parametrize(
    ("kwargs"),
    [
        (
            {
                "chunk_size": "50",
                "dry_run": "False",
                "output_file": "prsn_test_opendap.nc",
            }
        ),
    ],
)
def test_run_opendap(opendaps, kwargs):
    params = build_params(opendaps, kwargs)
    run_wps_process(GeneratePrsn(), params)


@pytest.mark.online
@pytest.mark.parametrize(
    ("netcdfs"),
    [nc_set for nc_set in netcdf_sets if not re.search("\S*/tiny_\S+.nc$", nc_set[0])],
)
@pytest.mark.parametrize(
    ("opendaps"), opendap_set,
)
@pytest.mark.parametrize(
    ("kwargs"),
    [
        (
            {
                "chunk_size": "100",
                "dry_run": "True",
                "output_file": "prsn_test_mixed1.nc",
            }
        ),
        (
            {
                "chunk_size": "100",
                "dry_run": "False",
                "output_file": "prsn_test_mixed2.nc",
            }
        ),
    ],
)
def test_run_mixed(netcdfs, opendaps, kwargs):
    mixed1 = (netcdfs[0], opendaps[1], opendaps[2])
    mixed2 = (opendaps[0], netcdfs[1], netcdfs[2])
    params1 = build_params(mixed1, kwargs)
    params2 = build_params(mixed2, kwargs)

    run_wps_process(GeneratePrsn(), params1)
    run_wps_process(GeneratePrsn(), params2)
