# Processor imports
from pywps import (
    Process,
    LiteralInput,
    ComplexInput,
    FORMATS,
)
from pywps.app.exceptions import ProcessError

# Tool imports
from dp.update_metadata import process_updates
from nchelpers import CFDataset
from wps_tools.utils import is_opendap_url, log_handler
from wps_tools.io import nc_output, log_level
from thunderbird.utils import logger

# Library imports
import shutil
import os
import yaml
import xarray as xr


class UpdateMetadata(Process):
    def __init__(self):
        self.status_percentage_steps = {
            "start": 0,
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
            ComplexInput(
                "updates",
                "Updates File(yaml)",
                abstract="The filepath of an updates file that specifies what to do to the metadata it finds in the NetCDF file",
                min_occurs=1,
                max_occurs=1,
                supported_formats=[FORMATS.TEXT],
            ),
            log_level,
        ]
        outputs = [nc_output]

        super(UpdateMetadata, self).__init__(
            self._handler,
            identifier="update_metadata",
            title="Update NetCDF Metadata",
            abstract="Update file containing missing, invalid, or incorrectly named global or variable metadata attributes",
            store_supported=True,
            status_supported=True,
            inputs=inputs,
            outputs=outputs,
        )

    def copy_and_get_filepath(self, request):
        """
        This function takes an input "request" and returns a filepath to the input data.
        As the update_metadata simply updates the original file "in place", copying the
        input data is necessary for two reasons.
        
        1. The original file is maintained without any corruption
        2. Writing back to OPeNDAP file is nearly impossible

        """
        path = request.inputs["netcdf"][0]
        if is_opendap_url(path.url):
            url = path.url
            input_dataset = xr.open_dataset(url)

            filename = url.split("/")[-1]
            original = os.path.join(self.workdir, filename)
            input_dataset.to_netcdf(original, format="NETCDF4_CLASSIC")

        elif path.file.endswith(".nc"):
            original = path.file

        else:
            raise ProcessError(
                f"You must provide a data source (opendap/netcdf). Inputs provided: {request.inputs}"
            )

        copy = original[:-3] + "_copy.nc"
        shutil.copyfile(original, copy)
        return copy

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

        filepath = self.copy_and_get_filepath(request)
        updates = request.inputs["updates"][0]
        logger.critical(updates.file)
        
        # determines if the input `updates` is a file or a string
        if os.path.isfile(updates.file):
            with open(updates) as ud:
                updates_instruction = yaml.safe_load(ud)
        else:
            updates_instruction = yaml.safe_load(updates)

        with CFDataset(filepath, mode="r+") as dataset:
            log_handler(
                self,
                response,
                f"Updating {filepath} metadata",
                logger,
                log_level=loglevel,
                process_step="process",
            )
            process_updates(dataset, updates_instruction)

        log_handler(
            self,
            response,
            "Building final output",
            logger,
            log_level=loglevel,
            process_step="build_output",
        )
        response.outputs["output"].file = filepath

        log_handler(
            self,
            response,
            "Process Complete",
            logger,
            log_level=loglevel,
            process_step="complete",
        )
        return response
