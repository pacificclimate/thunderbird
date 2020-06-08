import pytest

from pywps import Service
from pywps.tests import assert_response_success

from .common import client_for, TESTDATA
from thunderbird.processes.wps_generate_prsn import GeneratePrsn

def run(kwargs):
    client = client_for(Service(processes=[GeneratePrsn()]))
    if "chunk_size" in kwargs.keys() and "output_file" in kwargs.keys(): # Not using default values
        datainputs = (
        "prec=@xlink:href={prec};"
        "tasmin=@xlink:href={tasmin};"
        "tasmax=@xlink:href={tasmax};"
        "chunk_size={chunk_size};"
        "dry_run={dry_run};"
        "output_file={output_file};"
        ).format(**kwargs)
    else:
        datainputs = (
        "prec=@xlink:href={prec};"
        "tasmin=@xlink:href={tasmin};"
        "tasmax=@xlink:href={tasmax};"
        "dry_run={dry_run};"
        ).format(**kwargs)
    resp = client.get(
        service="wps",
        request="Execute",
        version="1.0.0",
        identifier="generate_prsn",
        datainputs=datainputs,
    )
    assert_response_success(resp)    
    
@pytest.mark.parametrize(
    ("kwargs"),
    [
        (
            {
                "prec": TESTDATA["test_local_pr_nc"],
                "tasmin": TESTDATA["test_local_tasmin_nc"],
                "tasmax": TESTDATA["test_local_tasmax_nc"],
                "dry_run": "True",
            }
        ),
    ],
)
def test_default_local(kwargs):
    run(kwargs)


@pytest.mark.parametrize(
    ("kwargs"),
    [
        (
            {
                "prec": TESTDATA["test_opendap_pr_nc"],
                "tasmin": TESTDATA["test_opendap_tasmin_nc"],
                "tasmax": TESTDATA["test_opendap_tasmax_nc"],
                "chunk_size": "50",
                "dry_run": "True",
                "output_file": "prsn_test_local.nc",
            }
        ),
    ],
)
def test_run_local(kwargs):
    run(kwargs)

@pytest.mark.online
@pytest.mark.parametrize(
    ("kwargs"),
    [
        (
            {
                "prec": TESTDATA["test_opendap_pr_nc"],
                "tasmin": TESTDATA["test_opendap_tasmin_nc"],
                "tasmax": TESTDATA["test_opendap_tasmax_nc"],
                "dry_run": "True",
            }
        ),
    ],
)
def test_default_opendap(kwargs):
    run(kwargs)

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
    run(kwargs)

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
    run(kwargs)
