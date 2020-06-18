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
from netCDF4 import Dataset
import numpy as np
import logging
import os
import sys

# Tool imports
from dp.decompose_flow_vectors import logger, decompose_flow_vectors
from thunderbird.utils import is_opendap_url


LOGGER = logging.getLogger("PYWPS")


class DecomposeFlowVectors(Process):
    def __init__(self):
        inputs = [
            ComplexInput(
                "netcdf",
                "Daily NetCDF Dataset",
                abstract="NetCDF file",
                min_occurs=1,
                max_occurs=1,
                supported_formats=[FORMATS.NETCDF, FORMATS.DODS],
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
        path = request.inputs["netcdf"][0]
        if is_opendap_url(path.url):
            return path.url
        elif path.file.endswith(".nc"):
            return path.file
        else:
            raise ProcessError(
                "You must provide a data source (opendap/netcdf). "
                f"Inputs provided: {request.inputs}"
            )

    def _handler(self, request, response):
        response.update_status("Starting Process", 0)

        source_file = self.get_filepath(request)
        variable = request.inputs["variable"][0].data
        dest_file = os.path.join(self.workdir, request.inputs["dest_file"][0].data)

        source = Dataset(source_file, "r", format="NETCDF4")

        if not "lon" in source.dimensions or not "lat" in source.dimensions:
            logger.debug(
                "{} does not have latitude and longitude dimensions".format(
                    source_file
                )
            )
            source.close()
            sys.exit()

        if not variable in source.variables:
            logger.debug(
                "Variable {} is not found in {}".format(variable, source_file)
            )
            source.close()
            sys.exit()

        flow_variable = source.variables[variable]

        if not "lon" in flow_variable.dimensions or not "lat" in flow_variable.dimensions:
            logger.debug("Variable {} is not associated with a grid".format(variable))
            source.close()
            sys.exit()

        if np.ma.max(flow_variable[:]) > 9 or np.ma.min(flow_variable[:]) < 1:
            logger.debug("Variable {} is not a valid flow routing".format(variable))
            source.close()
            sys.exit()

        decompose_flow_vectors(source, dest_file, variable)
        
        # args = arguments(source_file, variable, dest_file)
        # parser = ArgumentParserMocker()

        # dfv.main(args, parser)

        response.outputs["output"].file = dest_file

        response.update_status("Process Complete", 100)
        return response