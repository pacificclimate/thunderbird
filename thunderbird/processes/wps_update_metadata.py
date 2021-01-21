# Processor imports
from pywps import Process, LiteralInput, ComplexInput, FORMATS, Format, exceptions
from pywps.app.exceptions import ProcessError

# Tool imports
from dp.update_metadata import process_updates
from nchelpers import CFDataset
from wps_tools.logging import log_handler
from wps_tools.file_handling import is_opendap_url
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
                "updates_file",
                "Updates File(yaml)",
                abstract="The filepath of an updates file that specifies what to do to the metadata it finds in the NetCDF file",
                min_occurs=0,
                max_occurs=1,
                supported_formats=[Format(mime_type="text/x-yaml", extension=".yaml",)],
            ),
            LiteralInput(
                "updates_string",
                "Updates String(yaml format)",
                abstract="The string in yaml format that specifies what to do to the metadata it finds in the NetCDF file",
                min_occurs=0,
                max_occurs=1,
                data_type="string",
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
                "You must provide a data source (opendap/netcdf). Inputs provided"
            )

        copy = original[:-3] + "_copy.nc"
        shutil.copyfile(original, copy)
        return copy

    def updates_instruction_generator(self, request):
        """
        This function generates a dictionary containing the updates instruction information.
        The dictionary will be constructed using the content of the input updates_file/updates_string.
        It is desired that only one of the options is provided by the user, but if both are given,
        updates_file input will be used to generate while updates_string input will be neglected.

        There are odd behaviours of the ComplexInput updates_file; the content of the yaml file is
        directly accessible using the .data attribute when run in localhost while it is accessible
        as '.url' attribute when run in docker containers. When running pytest, the .data attribute
        holds the path to the origial file path.
        """
        if "updates_file" in request.inputs.keys():
            if vars(request.inputs["updates_file"][0])["_file"] != None:
                updates = request.inputs["updates_file"][
                    0
                ].file  # For running in localhost
            elif vars(request.inputs["updates_file"][0])["_data"] != None:
                updates = request.inputs["updates_file"][
                    0
                ].data  # For running in localhost
            else:
                updates = request.inputs["updates_file"][
                    0
                ].url  # For running in Docker containers
        elif "updates_string" in request.inputs.keys():
            updates = request.inputs["updates_string"][0].data

        # Convert yaml content to a dictionary
        if os.path.isfile(updates):  # For running pytest
            with open(updates) as ud:
                return yaml.safe_load(ud)
        else:
            return yaml.safe_load(updates)

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

        updates_instruction = self.updates_instruction_generator(request)

        filepath = self.copy_and_get_filepath(request)
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
