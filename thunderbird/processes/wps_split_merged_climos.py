# Processor imports
from pywps import (
    Process,
    LiteralInput,
    ComplexInput,
    ComplexOutput,
    FORMATS,
)
from pywps.app.Common import Metadata

# Tool imports
from nchelpers import CFDataset
from dp.split_merged_climos import split_merged_climos
from thunderbird.utils import (
    is_opendap_url,
    collect_output_files,
    build_meta_link,
    setup_logger,
)

# Library imports
import logging
import os
import math

logger = logging.getLogger("PYWPS")


class SplitMergedClimos(Process):
    def __init__(self):
        self.log_level_choices = [
            "NOTSET",
            "DEBUG",
            "INFO",
            "WARNING",
            "ERROR",
            "CRITICAL",
        ]
        inputs = [
            ComplexInput(
                "netcdf",
                "NetCDF Datasets",
                abstract="NetCDF files to process",
                min_occurs=1,
                max_occurs=100,
                supported_formats=[FORMATS.NETCDF, FORMATS.DODS],
            ),
            LiteralInput(
                "loglevel",
                "Log Level",
                default="INFO",
                abstract="Logging level",
                allowed_values=self.log_level_choices,
            ),
        ]
        outputs = [
            ComplexOutput(
                "output",
                "Output",
                abstract="Collection of split climatological files",
                as_reference=True,
                supported_formats=[FORMATS.META4],
            ),
        ]

        super(SplitMergedClimos, self).__init__(
            self._handler,
            identifier="split_merged_climos",
            title="Split Merged Climos",
            abstract="Create climatologies from CMIP5 data",
            metadata=[
                Metadata("NetCDF processing"),
                Metadata("Climate Data Operations"),
            ],
            inputs=inputs,
            outputs=outputs,
            store_supported=True,
            status_supported=True,
        )

    def get_filepaths(self, request):
        filepaths = []
        for path in request.inputs["netcdf"]:
            if is_opendap_url(path.url):
                filepaths.append(path.url)
            elif path.file.endswith(".nc"):
                filepaths.append(path.file)
            else:
                raise ProcessError(
                    "You must provide a data source (opendap/netcdf). "
                    f"Inputs provided: {request.inputs}"
                )
        return filepaths

    def _handler(self, request, response):
        response.update_status("Starting Process", 0)
        loglevel = request.inputs["loglevel"][0].data
        filepaths = self.get_filepaths(request)
        response.update_status("Processing files", 10)
        output_filepaths = []
        for path in filepaths:
            logger.info("")
            logger.info(f"Processing: {path}")
            try:
                input_file = CFDataset(path)
            except Exception as e:
                logger.info(f"{e.__class__.__name__}: {e}")
            else:
                output_filepaths.extend(split_merged_climos(input_file, self.workdir))

        response.update_status("File processing complete", 90)
        response.outputs["output"].data = build_meta_link(
            "split_climo", "Split climatologies", output_filepaths, self.workdir,
        )

        response.update_status("Process complete", 100)
        return response
