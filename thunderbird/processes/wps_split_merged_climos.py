# Processor imports
from pywps import (
    Process,
    ComplexInput,
    FORMATS,
)
from pywps.app.Common import Metadata
from pywps.app.exceptions import ProcessError

# Tool imports
from nchelpers import CFDataset
from dp.split_merged_climos import split_merged_climos
from thunderbird.utils import MAX_OCCURS, get_filepaths, build_meta_link, log_handler
from thunderbird.wps_io import log_level, meta4_output

# Library import
import logging


class SplitMergedClimos(Process):
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
                "NetCDF Datasets",
                abstract="NetCDF files to process",
                min_occurs=1,
                max_occurs=MAX_OCCURS,
                supported_formats=[FORMATS.NETCDF, FORMATS.DODS],
            ),
            log_level,
        ]
        outputs = [meta4_output]

        super(SplitMergedClimos, self).__init__(
            self._handler,
            identifier="split_merged_climos",
            title="Split Merged Climos",
            abstract="Split climo means files into one file per time interval",
            metadata=[
                Metadata("NetCDF processing"),
                Metadata("Climate Data Operations"),
            ],
            inputs=inputs,
            outputs=outputs,
            store_supported=True,
            status_supported=True,
        )

    def _handler(self, request, response):
        log_handler(self, response, "Starting Process", process_step="start")

        filepaths = get_filepaths(request)
        log_handler(
            self, response, f"Spliting climo files: {filepaths}", process_step="process"
        )
        output_filepaths = []
        for path in filepaths:
            try:
                input_file = CFDataset(path)
            except Exception:
                raise ProcessError(
                    f"The input file {path} could not be converted to a netcdf dataset"
                )
            else:
                output_filepaths.extend(split_merged_climos(input_file, self.workdir))

        log_handler(
            self, response, "Building final output", process_step="build_output"
        )
        response.outputs["output"].data = build_meta_link(
            varname="split_climo",
            desc="Split climatologies",
            outfiles=output_filepaths,
            outdir=self.workdir,
        )

        log_handler(self, response, "Process Complete", process_step="complete")
        return response
