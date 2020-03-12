from pywps import Service
from .common import client_for
from thunderbird.processes import processes
from owslib.wps import WebProcessingService


def test_describe():
    client = client_for(Service(processes=processes))
    resp = client.get(service='wps', request='describeprocess', identifier='all', version='1.0.0')
    wps = WebProcessingService("http://localhost", skip_caps=True)
    wps.describeprocess("all", xml=resp.data)
