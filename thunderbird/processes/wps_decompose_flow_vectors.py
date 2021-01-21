# Processor imports
from pywps import (
    Process,
    LiteralInput,
    ComplexInput,
    ComplexOutput,
    FORMATS,
)

# Library imports
from netCDF4 import Dataset
import os

# Tool imports
from dp.decompose_flow_vectors import (
    decompose_flow_vectors,
    source_check,
    variable_check,
)
from pywps.app.exceptions import ProcessError
from wps_tools.logging import log_handler
from wps_tools.file_handling import is_opendap_url
from wps_tools.io import log_level
from thunderbird.utils import logger


class DecomposeFlowVectors(Process):
    def __init__(self):
        self.status_percentage_steps = {
            "start": 0,
            "input_check": 5,
            "process": 10,
            "build_output": 95,
            "complete": 100,
        }
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
            log_level,
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
            raise ProcessError("You must provide a data source (opendap/netcdf).")

    def _handler(self, request, response):
        loglevel = request.inputs["loglevel"][0].data
        log_handler(
            self,
            response,
            "Starting Process",
            logger,
            log_level=loglevel,
            process_step="start",
        )

        source_file = self.get_filepath(request)
        print(source_file)
        variable = request.inputs["variable"][0].data
        dest_file = os.path.join(self.workdir, request.inputs["dest_file"][0].data)

        source = Dataset(source_file, "r", format="NETCDF4")

        log_handler(
            self,
            response,
            f"Checking {source_file} and {variable}",
            logger,
            log_level=loglevel,
            process_step="input_check",
        )
        try:
            source_check(source)
        except AttributeError as e:
            ProcessError("netcdf file does not have latitude and longitude dimensions")
        except ValueError as e:
            ProcessError("netcdf file does not have a valid flow variable")

        try:
            variable_check(source, variable)
        except AttributeError as e:
            raise ProcessError(
                f"Variable is either not found in netcdf file or is not associated with a grid"
            )
        except ValueError as e:
            raise ProcessError("Variable is not a valid flow routing")

        log_handler(
            self,
            response,
            "Decomposing flow direction vectors into grids",
            logger,
            log_level=loglevel,
            process_step="process",
        )

        try:
            decompose_flow_vectors(source, dest_file, variable)
        except Exception as e:
            raise ProcessError(f"{type(e).__name__}: {e}")

        log_handler(
            self,
            response,
            "Building final output",
            logger,
            log_level=loglevel,
            process_step="build_output",
        )
        response.outputs["output"].file = dest_file

        log_handler(
            self,
            response,
            "Process Complete",
            logger,
            log_level=loglevel,
            process_step="complete",
        )
        return response
