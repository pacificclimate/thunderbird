# Processor imports
from pywps import (
    Process,
    LiteralInput,
    ComplexInput,
    LiteralOutput,
    ComplexOutput,
    FORMATS,
    Format,
)
# Library imports
import logging
import os
import imp

def load_script(module, script):
    file_path = "/".join(module.__file__.split("/")[:-1]) + "/" + script
    return imp.load_source(script, file_path)

# Tool imports
from nchelpers import CFDataset
import scripts
dfv = load_script(scripts, "decompose_flow_vectors")


LOGGER = logging.getLogger("PYWPS")


class arguments:
    def __init__(self, source_file, variable, dest_file):
        self.source_file = source_file
        self.variable = variable
        self.dest_file = dest_file

class ArgumentParserMocker:
    def __init__(self):
        self.prog = 'decompose_flow_vectors'
        self.usage = None
        self.description = 'Process an indexed flow direction netCDF into a vectored netCDF suitable for ncWMS display'
        self.formatter_class= "<class 'argparse.HelpFormatter'>"
        self.conflict_handler= 'error'
        self.add_help=True

class DecomposeFlowVectors(Process):
    def __init__(self):
        inputs = [
            ComplexInput(
                "opendap",
                "source netCDF file",
                abstract="Path to OPEnDAP resource",
                min_occurs=0,
                max_occurs=1,
                supported_formats=[FORMATS.DODS],
            ),
            ComplexInput(
                "netcdf",
                "source netCDF file",
                abstract="Path to NetCDF file",
                min_occurs=0,
                max_occurs=1,
                supported_formats=[FORMATS.NETCDF],
            ),
            LiteralInput(
                "variable",
                "netCDF variable describing flow direction",
                data_type="string",
            ),
            LiteralInput(
                "dest_file",
                "destination netCDF file",
                data_type="string",
            ),
        ]
        outputs = [
            ComplexOutput(
                "output",
                "Output",
                abstract="output netCDF file",
                as_reference=True,
                supported_formats=[FORMATS.NETCDF],
            ),
        ]

        super(DecomposeFlowVectors, self).__init__(
            self._handler,
            identifier="decompose_flow_vectors",
            title="Update NetCDF Metadata",
            abstract="Process an indexed flow direction netCDF into a vectored netCDF suitable for ncWMS display",
            store_supported=True,
            status_supported=True,
            inputs=inputs,
            outputs=outputs,
        )

    def get_filepath(self, request):
        if "opendap" in request.inputs:
            return request.inputs["opendap"][0].url
        elif "netcdf" in request.inputs:
            return request.inputs["netcdf"][0].file
        else:
            raise ProcessError(
                f"You must provide a data source (opendap/netcdf). Inputs provided: {request.inputs}"
            )

    def _handler(self, request, response):
        response.update_status("Starting Process", 0)

        source_file = self.get_filepath(request)
        variable = request.inputs["variable"][0].data
        dest_file = request.inputs["dest_file"][0].data
        
        args = arguments(source_file, variable, dest_file)
        parser = ArgumentParserMocker()

        dfv.main(args, parser)

        response.outputs["output"].file = dest_file

        response.update_status("Process Complete", 100)
        return response