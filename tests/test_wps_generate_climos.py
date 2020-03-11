import pytest

from pywps import Service
from pywps.tests import assert_response_success

from .common import client_for, resource_file
from thunderbird.processes.wps_generate_climos import GenerateClimos
import owslib.wps

OPENDAP_URL = 'http://test.opendap.org:80/opendap/netcdf/examples/sresa1b_ncar_ccsm3_0_run1_200001.nc'
NC_URL = 'http://test.opendap.org:80/opendap/netcdf/examples/sresa1b_ncar_ccsm3_0_run1_200001.nc.nc4'
NC_FILE_URL = "file://{}".format(resource_file('test.nc'))


@pytest.mark.online
def test_wps_gen_climos_opendap():
    client = client_for(Service(processes=[GenerateClimos()]))
    datainputs = f"opendap=@xlink:href={OPENDAP_URL}"
    resp = client.get(
        service='wps', request='execute', version='1.0.0',
        identifier='generate_climos',
        datainputs=datainputs)
    assert_response_success(resp)
