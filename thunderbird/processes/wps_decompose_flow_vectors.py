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

    def source_check(self, source):
        source_file_path = source.filepath()

        if not "lon" in source.dimensions or not "lat" in source.dimensions:
            logger.critical(
                "{} does not have latitude and longitude dimensions".format(
                    source_file_path
                )
            )
            source.close("{} does not have latitude and longitude dimensions".format(
                    source_file_path
                )
            )
            raise ProcessError()

        valid_variables = []
        for v in source.variables:
            variable = source.variables[v]
            if (
                hasattr(variable, "dimensions")
                and "lon" in variable.dimensions
                and "lat" in variable.dimensions
            ):
                if np.ma.max(variable[:]) <= 9 and np.ma.min(variable[:]) >= 1:
                    valid_variables.append(v)

        if len(valid_variables) == 0:
            logger.critical(
                "{} does not have a valid flow variable".format(source_file_path)
            )
            source.close()
            raise ProcessError("{} does not have a valid flow variable".format(source_file_path))

    def variable_check(self, source, variable):
        source_file_path = source.filepath()

        if not variable in source.variables:
            logger.critical(
                "Variable {} is not found in {}".format(variable, source_file_path)
            )
            source.close()
            raise ProcessError("Variable {} is not found in {}".format(variable, source_file_path))

        flow_variable = source.variables[variable]

        if (
            not "lon" in flow_variable.dimensions
            or not "lat" in flow_variable.dimensions
        ):
            logger.critical("Variable {} is not associated with a grid".format(variable))
            source.close()
            raise ProcessError("Variable {} is not associated with a grid".format(variable))

        if np.ma.max(flow_variable[:]) > 9 or np.ma.min(flow_variable[:]) < 1:
            logger.critical("Variable {} is not a valid flow routing".format(variable))
            source.close()
            raise ProcessError("Variable {} is not associated with a grid".format(variable))

    def _handler(self, request, response):
        response.update_status("Starting Process", 0)

        source_file = self.get_filepath(request)
        variable = request.inputs["variable"][0].data
        dest_file = os.path.join(self.workdir, request.inputs["dest_file"][0].data)

        source = Dataset(source_file, "r", format="NETCDF4")
        self.source_check(source)
        self.variable_check(source, variable)

        decompose_flow_vectors(source, dest_file, variable)

        response.outputs["output"].file = dest_file

        response.update_status("Process Complete", 100)
        return response
