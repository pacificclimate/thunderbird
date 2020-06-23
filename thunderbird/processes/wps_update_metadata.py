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
from thunderbird.utils import is_opendap_url
from thunderbird.wps_io import ncOutput

# Library imports
import shutil
import os
import yaml
import xarray as xr


class UpdateMetadata(Process):
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
                "updates",
                "Updates File(yaml)",
                abstract="The filepath of an updates file that specifies what to do to the metadata it finds in the NetCDF file",
                min_occurs=1,
                max_occurs=1,
                data_type="string",
            ),
        ]
        outputs = [ncOutput]

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
        response.update_status("Starting Process", 0)

        filepath = self.copy_and_get_filepath(request)
        response.update_status(f"Processing {filepath}", 10)

        updates = request.inputs["updates"][0].data

        # determines if the input `updates` is a file or a string
        if os.path.isfile(updates):
            with open(updates) as ud:
                updates_instruction = yaml.safe_load(ud)
        else:
            updates_instruction = yaml.safe_load(updates)

        with CFDataset(filepath, mode="r+") as dataset:
            process_updates(dataset, updates_instruction)

        response.outputs["output"].file = filepath

        response.update_status("Process Complete", 100)
        return response
