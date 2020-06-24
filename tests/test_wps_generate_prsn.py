import pytest

from pywps import Service
from pywps.tests import assert_response_success

from .common import TESTDATA, run_wps_process
from thunderbird.processes.wps_generate_prsn import GeneratePrsn


def build_params(kwargs):
    if (
        "chunk_size" in kwargs.keys() and "output_file" in kwargs.keys()
    ):  # Not using default values
        return (
            "prec=@xlink:href={prec};"
            "tasmin=@xlink:href={tasmin};"
            "tasmax=@xlink:href={tasmax};"
            "chunk_size={chunk_size};"
            "dry_run={dry_run};"
            "output_file={output_file};"
        ).format(**kwargs)
    else:
        return (
            "prec=@xlink:href={prec};"
            "tasmin=@xlink:href={tasmin};"
            "tasmax=@xlink:href={tasmax};"
            "dry_run={dry_run};"
        ).format(**kwargs)


@pytest.mark.parametrize(
    ("kwargs"),
    [
        (
            {
                "prec": TESTDATA["test_local_pr_nc"],
                "tasmin": TESTDATA["test_local_tasmin_nc"],
                "tasmax": TESTDATA["test_local_tasmax_nc"],
                "dry_run": "False",
            }
        ),
    ],
)
def test_default_local(kwargs):
    params = build_params(kwargs)
    run_wps_process(GeneratePrsn(), params)


@pytest.mark.parametrize(
    ("kwargs"),
    [
        (
            {
                "prec": TESTDATA["test_local_pr_nc"],
                "tasmin": TESTDATA["test_local_tasmin_nc"],
                "tasmax": TESTDATA["test_local_tasmax_nc"],
                "chunk_size": "50",
                "dry_run": "True",
                "output_file": "prsn_test_local.nc",
            }
        ),
    ],
)
def test_run_local(kwargs):
    params = build_params(kwargs)
    run_wps_process(GeneratePrsn(), params)


@pytest.mark.online
@pytest.mark.parametrize(
    ("kwargs"),
    [
        (
            {
                "prec": TESTDATA["test_opendap_pr_nc"],
                "tasmin": TESTDATA["test_opendap_tasmin_nc"],
                "tasmax": TESTDATA["test_opendap_tasmax_nc"],
                "dry_run": "False",
            }
        ),
    ],
)
def test_default_opendap(kwargs):
    params = build_params(kwargs)
    run_wps_process(GeneratePrsn(), params)


@pytest.mark.online
@pytest.mark.parametrize(
    ("kwargs"),
    [
        (
            {
                "prec": TESTDATA["test_opendap_pr_nc"],
                "tasmin": TESTDATA["test_opendap_tasmin_nc"],
                "tasmax": TESTDATA["test_opendap_tasmax_nc"],
                "chunk_size": "50",
                "dry_run": "False",
                "output_file": "prsn_test_opendap.nc",
            }
        ),
    ],
)
def test_run_opendap(kwargs):
    params = build_params(kwargs)
    run_wps_process(GeneratePrsn(), params)


@pytest.mark.online
@pytest.mark.parametrize(
    ("kwargs"),
    [
        (
            {
                "prec": TESTDATA["test_local_pr_nc"],
                "tasmin": TESTDATA["test_opendap_tasmin_nc"],
                "tasmax": TESTDATA["test_opendap_tasmax_nc"],
                "chunk_size": "100",
                "dry_run": "True",
                "output_file": "prsn_test_mixed1.nc",
            }
        ),
        (
            {
                "prec": TESTDATA["test_opendap_pr_nc"],
                "tasmin": TESTDATA["test_local_tasmin_nc"],
                "tasmax": TESTDATA["test_local_tasmax_nc"],
                "chunk_size": "100",
                "dry_run": "False",
                "output_file": "prsn_test_mixed2.nc",
            }
        ),
    ],
)
def test_run_mixed(kwargs):
    params = build_params(kwargs)
    run_wps_process(GeneratePrsn(), params)
