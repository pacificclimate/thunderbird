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
        "kwargs"
    ),
    [
        ({"operation":"mean", "climo":"6190", "resolutions":"yearly", "convert_longitudes":"True", "split_vars":"True", "split_intervals":"True", "dry_run":"False"}),
        ({"operation":"std", "climo":"7100", "resolutions":"seasonal", "convert_longitudes":"False", "split_vars":"False", "split_intervals":"False", "dry_run":"True"}),
    ],
)
def test_wps_gen_climos_opendap(opendap, kwargs):
    client = client_for(Service(processes=[GenerateClimos()]))
    datainputs = (
        "opendap=@xlink:href={0};"
        "operation={operation};"
        "climo={climo};"
        "resolutions={resolutions};"
        "convert_longitudes={convert_longitudes};"
        "split_vars={split_vars};"
        "split_intervals={split_intervals};"
        "dry_run={dry_run};"
    ).format(opendap, **kwargs)

    resp = client.get(
        service="wps",
        request="Execute",
        version="1.0.0",
        identifier="generate_climos",
        datainputs=datainputs,
    )
    assert_response_success(resp)
