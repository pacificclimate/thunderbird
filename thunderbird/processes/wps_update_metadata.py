# Processor imports
from pywps import (
    Process,
    LiteralInput,
    ComplexInput,
    ComplexOutput,
    FORMATS,
    Format,
)

# Tool imports
from dp.update_metadata import process_updates, logger
from nchelpers import CFDataset

# Library imports
import shutil
import logging
import os
import netCDF4 as nc
import yaml
import xarray as xr

LOGGER = logging.getLogger("PYWPS")


class UpdateMetadata(Process):
    def __init__(self):

        inputs = [
            ComplexInput(
                "opendap",
                "Daily NetCDF Dataset",
                abstract="Path to OpenDAP resource",
                min_occurs=0,
                max_occurs=1,
                supported_formats=[FORMATS.DODS],
            ),
            ComplexInput(
                "netcdf",
                "Daily NetCDF Dataset",
                abstract="NetCDF file",
                min_occurs=0,
                max_occurs=1,
                supported_formats=[FORMATS.NETCDF],
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
        outputs = [
            ComplexOutput(
                "output",
                "Output",
                abstract="Updated NetCDF files",
                as_reference=True,
                supported_formats=[FORMATS.NETCDF],
            ),
        ]

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
        '''
        This function takes an input "request" and returns a filepath to the input data.
        As the update_metadata simply updates the original file "in place", copying the
        input data is necessary for two reasons.
        
        1. The original file is maintained without any corruption
        2. Writing back to OPeNDAP file is nearly impossible

        '''
        if "opendap" in request.inputs: 
            url = request.inputs["opendap"][0].url
            input_dataset = xr.open_dataset(url)

            filename = url.split("/")[-1]
            original = os.path.join(self.workdir, filename)
            input_dataset.to_netcdf(original, format = "NETCDF4_CLASSIC")

        elif "netcdf" in request.inputs:
            original = request.inputs["netcdf"][0].file

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

        try:
            with open(updates) as ud:
                updates_instruction = yaml.safe_load(ud)

        except FileNotFoundError:
            updates_yaml = os.path.join(self.workdir, "updates.yaml")
    
            with open(updates_yaml, "w+") as yamlfile:
                yamlfile.write(updates)
            with open(updates_yaml) as ud:
                updates_instruction = yaml.safe_load(ud)

        with CFDataset(filepath, mode='r+') as dataset:
            process_updates(dataset, updates_instruction)


        response.outputs["output"].file = filepath

        response.update_status("Process Complete", 100)
        return response