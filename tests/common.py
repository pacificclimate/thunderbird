from pywps.app.basic import get_xpath_ns
from pywps.tests import WpsClient, WpsTestResponse
import os

VERSION = "1.0.0"
xpath_ns = get_xpath_ns(VERSION)
TESTS_HOME = os.path.abspath(os.path.dirname(__file__))


def resource_file(filepath):
    return os.path.join(TESTS_HOME, "testdata", filepath)


TESTDATA = {
    "test_local_nc": "file:///{}".format(resource_file("test.nc")),
    "test_opendap": "http://test.opendap.org:80/opendap/netcdf/examples/sresa1b_ncar_ccsm3_0_run1_200001.nc",
    "test_local_pr_nc": "file:///{}".format(
        os.path.abspath("tests/data/pr_week_test.nc")
    ),
    "test_local_tasmin_nc": "file:///{}".format(
        os.path.abspath("tests/data/tasmin_week_test.nc")
    ),
    "test_local_tasmax_nc": "file:///{}".format(
        os.path.abspath("tests/data/tasmax_week_test.nc")
    ),
    "test_opendap_pr_nc": "http://docker-dev03.pcic.uvic.ca:8083/twitcher/ows/proxy/thredds/dodsC/datasets/TestData/pr_day_BCCAQv2+ANUSPLIN300_NorESM1-M_historical+rcp26_r1i1p1_19500101-19501231.nc",
    "test_opendap_tasmin_nc": "http://docker-dev03.pcic.uvic.ca:8083/twitcher/ows/proxy/thredds/dodsC/datasets/TestData/tasmin_day_BCCAQv2+ANUSPLIN300_NorESM1-M_historical+rcp26_r1i1p1_19500101-19501231.nc",
    "test_opendap_tasmax_nc": "http://docker-dev03.pcic.uvic.ca:8083/twitcher/ows/proxy/thredds/dodsC/datasets/TestData/tasmax_day_BCCAQv2+ANUSPLIN300_NorESM1-M_historical+rcp26_r1i1p1_19500101-19501231.nc",
}


class WpsTestClient(WpsClient):
    def get(self, *args, **kwargs):
        query = "?"
        for key, value in kwargs.items():
            query += "{0}={1}&".format(key, value)
        return super(WpsTestClient, self).get(query)


def client_for(service):
    return WpsTestClient(service, WpsTestResponse)


def get_output(doc):
    """Copied from pywps/tests/test_execute.py.
    TODO: make this helper method public in pywps."""
    output = {}
    for output_el in xpath_ns(
        doc, "/wps:ExecuteResponse" "/wps:ProcessOutputs/wps:Output"
    ):
        [identifier_el] = xpath_ns(output_el, "./ows:Identifier")

        lit_el = xpath_ns(output_el, "./wps:Data/wps:LiteralData")
        if lit_el != []:
            output[identifier_el.text] = lit_el[0].text

        ref_el = xpath_ns(output_el, "./wps:Reference")
        if ref_el != []:
            output[identifier_el.text] = ref_el[0].attrib["href"]

        data_el = xpath_ns(output_el, "./wps:Data/wps:ComplexData")
        if data_el != []:
            output[identifier_el.text] = data_el[0].text

    return output
