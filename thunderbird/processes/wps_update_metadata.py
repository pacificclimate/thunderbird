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

from pywps.app.Common import Metadata
from pywps.inout.outputs import MetaLink, MetaLink4, MetaFile
from pywps.inout.literaltypes import AllowedValue
from pywps.validator.mode import MODE
from pywps.app.exceptions import ProcessError

from argparse import ArgumentParser

# Tool imports
from nchelpers import CFDataset
from dp.update_metadata import process_updates, logger
from dp.argparse_helpers import log_level_choices

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
                "Updates File",
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
            title="Update NetCDF file",
            abstract="Update file containing missing, invalid, or incorrectly named global or variable metadata attributes",
            store_supported=True,
            status_supported=True,
            inputs=inputs,
            outputs=outputs,
        )


    def get_filepath_and_copy(self, request):
        if "opendap" in request.inputs: 
            url = request.inputs["opendap"][0].url
            input_dataset = xr.open_dataset(url)

            filename = url.split("/")[-1]
            original = os.path.join(self.workdir, filename)

            input_dataset.to_netcdf(original)

            copy = original[:-3] + "_copy.nc"
            shutil.copyfile(original, copy)

            return copy

        elif "netcdf" in request.inputs:
            original = request.inputs["netcdf"][0].file
            copy = original[:-3] + "_copy.nc"
            shutil.copyfile(original, copy)
            return copy

        else:
            raise ProcessError(
                f"You must provide a data source (opendap/netcdf). Inputs provided: {request.inputs}"
            )

    def _handler(self, request, response):
        response.update_status("Starting Process", 0)

        filepath = self.get_filepath_and_copy(request)
        response.update_status(f"Processing {filepath}", 10)

        updates = request.inputs["updates"][0].data

        with open(updates) as ud:
            updates = yaml.safe_load(ud)

        with CFDataset(filepath, mode='r+') as dataset:
            process_updates(dataset, updates)

        response.outputs["output"].file = filepath

        response.update_status("Process Complete", 100)
        return response