# Processor imports
from pywps import (
    Process,
    LiteralInput,
    ComplexInput,
    FORMATS,
)
from pywps.app.Common import Metadata
from pywps.app.exceptions import ProcessError

# Tool imports
from dp.generate_prsn import generate_prsn_file
from dp.generate_prsn import dry_run as dry_run_info
from thunderbird.utils import (
    is_opendap_url,
    collect_output_files,
    build_meta_link,
    setup_logger,
)
from thunderbird.wps_io import (
    log_level,
    dryrun_input,
    nc_output,
    dryrun_output,
)

# Library imports
import logging
import os

logger = logging.getLogger("PYWPS")


class GeneratePrsn(Process):
    def __init__(self):
        inputs = [
            ComplexInput(
                "prec",
                "Precipitation",
                abstract="Precipitation file to process",
                min_occurs=1,
                max_occurs=1,
                supported_formats=[FORMATS.NETCDF, FORMATS.DODS],
            ),
            ComplexInput(
                "tasmin",
                "Tasmin",
                abstract="Tasmin file to process",
                min_occurs=1,
                max_occurs=1,
                supported_formats=[FORMATS.NETCDF, FORMATS.DODS],
            ),
            ComplexInput(
                "tasmax",
                "Tasmax",
                abstract="Tasmax file to process",
                min_occurs=1,
                max_occurs=1,
                supported_formats=[FORMATS.NETCDF, FORMATS.DODS],
            ),
            LiteralInput(
                "chunk_size",
                "Chunk Size",
                default=100,
                abstract="Number of time slices to be read/written at a time",
                data_type="integer",
            ),
            LiteralInput(
                "output_file",
                "Output File",
                default="None",
                abstract="Optional custom name of output file",
                data_type="string",
            ),
            log_level,
            dryrun_input,
        ]
        outputs = [
            nc_output,
            dryrun_output,
        ]

        super(GeneratePrsn, self).__init__(
            self._handler,
            identifier="generate_prsn",
            title="Generate Precipitation as Snow",
            abstract="Generate precipitation as snow file from precipitation "
            "and minimum/maximum temperature data",
            metadata=[
                Metadata("NetCDF processing"),
                Metadata("Climate Data Operations"),
            ],
            inputs=inputs,
            outputs=outputs,
            store_supported=True,
            status_supported=True,
        )

    def collect_args(self, request):
        chunk_size = request.inputs["chunk_size"][0].data
        loglevel = request.inputs["loglevel"][0].data
        dry_run = request.inputs["dry_run"][0].data
        output_file = request.inputs["output_file"][0].data
        if output_file == "None":
            output_file = None
            # generate_prsn_file uses NoneType to indicate no custom output file name
        return (
            chunk_size,
            loglevel,
            dry_run,
            output_file,
        )

    def get_filepaths(self, request):
        filepaths = {}
        var_list = ["pr", "tasmin", "tasmax"]
        data_files = [
            request.inputs["prec"][0],
            request.inputs["tasmin"][0],
            request.inputs["tasmax"][0],
        ]
        for var, path in zip(var_list, data_files):
            if is_opendap_url(path.url):
                filepaths[var] = path.url
            elif path.file.endswith(".nc"):
                filepaths[var] = path.file
            else:
                raise ProcessError(
                    "You must provide a data source (opendap/netcdf). "
                    f"Inputs provided: {request.inputs}"
                )
        return filepaths

    def _handler(self, request, response):
        response.update_status("Starting Process", 0)

        (chunk_size, loglevel, dry_run, output_file) = self.collect_args(request)
        filepaths = self.get_filepaths(request)
        setup_logger(logger, loglevel)

        if dry_run:
            response.update_status("Dry Run", 10)
            del response.outputs["output"]  # remove unnecessary output
            dry_output_path = os.path.join(self.workdir, "dry.txt")
            dry_run_info(filepaths, dry_output_path)
            response.outputs["dry_output"].file = dry_output_path

        else:
            del response.outputs["dry_output"]  # remove unnecessary output

            response.update_status("Processing files", 10)
            generate_prsn_file(filepaths, chunk_size, self.workdir, output_file)

            response.update_status("File processing complete", 90)
            prsn_file = collect_output_files("prsn", self.workdir)[0]

            response.update_status("Collecting output file", 95)
            response.outputs["output"].file = os.path.join(self.workdir, prsn_file)

        response.update_status("Process complete", 100)
        return response
