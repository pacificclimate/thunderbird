from pkg_resources import resource_filename
from pywps.app.basic import get_xpath_ns
from pywps.tests import WpsClient, WpsTestResponse

import pkg_resources

VERSION = "1.0.0"
xpath_ns = get_xpath_ns(VERSION)

test_files = [
    "file:///{}".format(pkg_resources.resource_filename(__name__, "data/" + test_file))
    for test_file in pkg_resources.resource_listdir(__name__, "data")
    if test_file.startswith("tiny_")
]

yaml_files = [
    pkg_resources.resource_filename(__name__, "metadata-conversion/" + test_file)
    for test_file in pkg_resources.resource_listdir(__name__, "metadata-conversion")
]
yaml_str = [
    """
global:
    history: "today is a nice day"
"""
]

TESTDATA = {
    "test_local_nc": test_files,
    "test_opendap": "http://docker-dev03.pcic.uvic.ca/twitcher/ows/proxy/thredds/dodsC/datasets/TestData/fdd_seasonal_CanESM2_rcp85_r1i1p1_1951-2100.nc",
    "test_local_pr_nc": "file:///{}".format(
        resource_filename("tests", "data/pr_week_test.nc")
    ),
    "test_local_tasmin_nc": "file:///{}".format(
        resource_filename("tests", "data/tasmin_week_test.nc")
    ),
    "test_local_tasmax_nc": "file:///{}".format(
        resource_filename("tests", "data/tasmax_week_test.nc")
    ),
    "test_opendap_pr_nc": "http://docker-dev03.pcic.uvic.ca:8083/twitcher/ows/"
    "proxy/thredds/dodsC/datasets/TestData/"
    "pr_day_BCCAQv2%2BANUSPLIN300_NorESM1-M_historical%2Brcp26_"
    "r1i1p1_19500101-19500107.nc",
    "test_opendap_tasmin_nc": "http://docker-dev03.pcic.uvic.ca:8083/twitcher/ows/"
    "proxy/thredds/dodsC/datasets/TestData/"
    "tasmin_day_BCCAQv2%2BANUSPLIN300_NorESM1-M_historical%2Brcp26_"
    "r1i1p1_19500101-19500107.nc",
    "test_opendap_tasmax_nc": "http://docker-dev03.pcic.uvic.ca:8083/twitcher/ows/"
    "proxy/thredds/dodsC/datasets/TestData/"
    "tasmax_day_BCCAQv2%2BANUSPLIN300_NorESM1-M_historical%2Brcp26_"
    "r1i1p1_19500101-19500107.nc",
    "test_yaml": yaml_files + yaml_str,
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
