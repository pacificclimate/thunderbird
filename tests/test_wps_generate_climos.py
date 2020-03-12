import pytest

from pywps import Service
from pywps.tests import assert_response_success

from .common import client_for, TESTDATA
from thunderbird.processes.wps_generate_climos import GenerateClimos
import owslib.wps


@pytest.mark.online
@pytest.mark.parametrize(
    ("opendap"), [(TESTDATA["test_opendap"])],
)
@pytest.mark.parametrize(
    (
        "operation",
        "climo",
        "resolutions",
        "convert_longitudes",
        "split_vars",
        "split_intervals",
        "dry_run",
    ),
    [
        ("mean", "6190", "yearly", "True", "True", "True", "False"),
        ("std", "7100", "seasonal", "False", "False", "False", "True"),
    ],
)
def test_wps_gen_climos_opendap(
    opendap,
    operation,
    climo,
    resolutions,
    convert_longitudes,
    split_vars,
    split_intervals,
    dry_run,
):
    client = client_for(Service(processes=[GenerateClimos()]))
    datainputs = (
        f"opendap=@xlink:href={opendap};"
        f"operation={operation};"
        f"climo={climo};"
        f"resolutions={resolutions};"
        f"convert_longitudes={convert_longitudes};"
        f"split_vars={split_vars};"
        f"split_intervals={split_intervals};"
        f"dry_run={dry_run};"
    )
    resp = client.get(
        service="wps",
        request="Execute",
        version="1.0.0",
        identifier="generate_climos",
        datainputs=datainputs,
    )
    assert_response_success(resp)
