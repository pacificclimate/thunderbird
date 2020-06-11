from pywps import get_ElementMakerForVersion
from pywps.app.basic import get_xpath_ns
from pywps.tests import WpsClient, WpsTestResponse

import pkg_resources

VERSION = "1.0.0"
xpath_ns = get_xpath_ns(VERSION)

test_files = ["file:///{}".format(pkg_resources.resource_filename("tests", "data/"+test_file)) 
                for test_file in pkg_resources.resource_listdir("tests", "data")]

yaml_files = [pkg_resources.resource_filename("tests", "metadata-conversion/"+test_file)
                for test_file in pkg_resources.resource_listdir("tests", "metadata-conversion")]
yaml_str = [        
"""
global:
    history: "today is a nice day"
"""
]

TESTDATA = {
    "test_local_nc": test_files,
    "test_opendap": "http://test.opendap.org:80/opendap/netcdf/examples/sresa1b_ncar_ccsm3_0_run1_200001.nc",
    "test_yaml": yaml_files + yaml_str
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
