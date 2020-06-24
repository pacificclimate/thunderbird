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
from dp.decompose_flow_vectors import (
    logger,
    decompose_flow_vectors,
    source_check,
    variable_check,
)
from pywps.app.exceptions import ProcessError
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
            LiteralInput("dest_file", "destination netCDF file", data_type="string",),
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
        try:
            source_check(source)
            variable_check(source, variable)
        except (AttributeError, ValueError) as e:
            raise ProcessError(e.args[0])

        decompose_flow_vectors(source, dest_file, variable)

        response.outputs["output"].file = dest_file

        response.update_status("Process Complete", 100)
        return response
