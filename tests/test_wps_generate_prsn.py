import pytest
import os

from pywps import Service
from pywps.tests import assert_response_success

from .common import client_for, TESTDATA
from thunderbird.processes.wps_generate_prsn import GeneratePrsn
import owslib.wps

#@pytest.mark.online
@pytest.mark.parametrize(
    ("kwargs"),
    [
        (
            {
                "prec": TESTDATA["test_local_pr_nc"],
                "tasmin": TESTDATA["test_local_tasmin_nc"],
                "tasmax": TESTDATA["test_local_tasmax_nc"],
                "dry_run": "False",
                "output_file": "prsn_test1.nc",
            }
        ),
        #(
        #    {
        #        "prec": TESTDATA["test_opendap_pr_nc"],
        #        "tasmin": TESTDATA["test_opendap_tasmin_nc"],
        #        "tasmax": TESTDATA["test_opendap_tasmax_nc"],
        #        "dry_run": "False",
        #        "output_file": "prsn_test2.nc",
        #    }
        #),
        #(
        #    {
        #        "prec": TESTDATA["test_local_pr_nc"],
        #        "tasmin": TESTDATA["test_opendap_tasmin_nc"],
        #        "tasmax": TESTDATA["test_local_tasmax_nc"],
        #        "dry_run": "False",
        #        "output_file": "prsn_test3.nc",
        #    }
        #),
        #(
        #    {
        #        "prec": TESTDATA["test_local_pr_nc"],
        #        "tasmin": TESTDATA["test_opendap_tasmin_nc"],
        #        "tasmax": TESTDATA["test_opendap_tasmax_nc"],
        #        "dry_run": "False",
        #        "output_file": "prsn_test4.nc",
        #    }
        #),
    ],
)
def test_runs(kwargs):
    client = client_for(Service(processes=[GeneratePrsn()]))
    datainputs = (
        "prec={prec};"
        "tasmin={tasmin};"
        "tasmax={tasmax};"
        "dry_run={dry_run};"
        "output_file={output_file};"
    ).format(**kwargs)
    resp = client.get(
        service="wps",
        request="Execute",
        version="1.0.0",
        identifier="generate_prsn",
        datainputs=datainputs,
    )
    assert_response_success(resp)
    
    

