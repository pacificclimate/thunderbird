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
from dp.generate_prsn import dry_run
from thunderbird.utils import (
    is_opendap_url,
    collect_output_files,
    build_meta_link,
    log_handler,
)
from thunderbird.wps_io import (
    log_level,
    dryrun_input,
    nc_output,
    dryrun_output,
)

# Library imports
import os
import logging


class GeneratePrsn(Process):
    def __init__(self):
        self.status_percentage_steps = {
            "start": 0,
            "dry_run": 5,
            "process": 10,
            "collect_files": 90,
            "build_output": 95,
            "complete": 100,
        }
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

    def dry_run_info(self, filepaths):
        '''
        This function creates an output file "dry.txt".
        logging.basicConfig() is used to redirect messages logged from
        generate_prsn's dry_run to the created file. After dry_run
        is processed, logging.root.removeHandler(handler) resets logging 
        configuration to redirect further logging messages to terminal.
        '''
        filename = os.path.join(self.workdir, "dry.txt")
        with open(filename, "w") as f:
            f.write("Dry Run\n")
            logging.basicConfig(filename=filename, level=logging.INFO)
            dry_run(filepaths)
            for handler in logging.root.handlers[:]:
                logging.root.removeHandler(handler)

        return filename

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
        (chunk_size, loglevel, dry_run, output_file) = self.collect_args(request)
        log_handler(
            self, response, "Starting Process", process_step="start", level=loglevel
        )

        filepaths = self.get_filepaths(request)

        if dry_run:
            log_handler(
                self, response, "Dry Run", process_step="dry_run", level=loglevel
            )
            del response.outputs["output"]  # remove unnecessary output
            dry_file = self.dry_run_info(filepaths)
            response.outputs["dry_output"].file = dry_file

        else:
            del response.outputs["dry_output"]  # remove unnecessary output

            log_handler(
                self,
                response,
                f"Processing {filepaths} into snowfall fluxes",
                process_step="process",
                level=loglevel,
            )
            generate_prsn_file(filepaths, chunk_size, self.workdir, output_file)

            log_handler(
                self,
                response,
                "Collecting snowfall files",
                process_step="collect_files",
                level=loglevel,
            )
            (prsn_file,) = collect_output_files("prsn", self.workdir)

            log_handler(
                self,
                response,
                "Building final output",
                process_step="build_output",
                level=loglevel,
            )
            response.outputs["output"].file = os.path.join(self.workdir, prsn_file)

        log_handler(
            self, response, "Process Complete", process_step="complete", level=loglevel,
        )
        return response
