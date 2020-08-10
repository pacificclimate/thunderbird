# Processor imports
from pywps import (
    Process,
    LiteralInput,
    ComplexInput,
    FORMATS,
)
from pywps.app.Common import Metadata

# Tool imports
from nchelpers import CFDataset, standard_climo_periods
from dp.generate_climos import generate_climos, dry_run_handler
from wps_tools.utils import (
    MAX_OCCURS,
    get_filepaths,
    collect_output_files,
    build_meta_link,
    log_handler,
)
from wps_tools.io import (
    dryrun_input,
    meta4_output,
    meta4_dryrun_output,
    log_level,
)
from thunderbird.dry_run_utils import dry_run_info, dry_output_filename

# Library imports
import logging
import os


class GenerateClimos(Process):
    def __init__(self):
        self.climos = list(standard_climo_periods().keys())
        self.resolutions = [
            "yearly",
            "seasonal",
            "monthly",
        ]
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
                "netcdf",
                "Daily NetCDF Dataset",
                abstract="NetCDF file",
                min_occurs=1,
                max_occurs=MAX_OCCURS,
                supported_formats=[FORMATS.NETCDF, FORMATS.DODS],
            ),
            LiteralInput(
                "operation",
                "Data Operation",
                abstract="Operation to perform on the datasets",
                allowed_values=["mean", "std"],
                data_type="string",
            ),
            LiteralInput(
                "climo",
                "Climatological Period",
                abstract="Year ranges",
                min_occurs=0,
                mode=0,
                allowed_values=self.climos,
                data_type="string",
            ),
            LiteralInput(
                "resolutions",
                "Temporal Resolutions",
                min_occurs=0,
                max_occurs=3,
                allowed_values=["all"] + self.resolutions,
                data_type="string",
            ),
            LiteralInput(
                "convert_longitudes",
                "Convert Longitudes",
                default=True,
                abstract="Transform longitude range from [0, 360) to [-180, 180)",
                data_type="boolean",
            ),
            LiteralInput(
                "split_vars",
                "Split Variables",
                default=True,
                abstract="Generate a separate file for each "
                "dependent variable in the file",
                data_type="boolean",
            ),
            LiteralInput(
                "split_intervals",
                "Split Intervals",
                default=True,
                abstract="Generate a separate file for each climatological period",
                data_type="boolean",
            ),
            dryrun_input,
            log_level,
        ]
        outputs = [
            meta4_output,
            meta4_dryrun_output,
        ]

        super(GenerateClimos, self).__init__(
            self._handler,
            identifier="generate_climos",
            version="0.7.0",
            title="Generate Climatological Means",
            abstract="Generate files containing climatological means from "
            "input files of daily, monthly, or yearly data that adhere "
            "to the PCIC metadata standard (and consequently to "
            "CMIP5 and CF standards).",
            metadata=[
                Metadata("NetCDF processing"),
                Metadata("Climate Data Operations"),
            ],
            inputs=inputs,
            outputs=outputs,
            store_supported=True,
            status_supported=True,
        )

    def get_identifier(self, operation):
        """Use operation in filename to indicate that it is an output file"""
        suffix = {"mean": "Mean", "std": "SD"}[operation]
        return "Clim" + suffix

    def collect_args(self, request):
        if "climo" in request.inputs:
            climo = list(set([climo.data for climo in request.inputs["climo"]]))
        else:
            climo = self.climos

        if "resolutions" in request.inputs:
            resolutions = list(
                set([resolution.data for resolution in request.inputs["resolutions"]])
            )
        else:
            resolutions = self.resolutions

        operation = request.inputs["operation"][0].data
        convert_longitudes = request.inputs["convert_longitudes"][0].data
        split_vars = request.inputs["split_vars"][0].data
        split_intervals = request.inputs["split_intervals"][0].data
        dry_run = request.inputs["dry_run"][0].data
        loglevel = request.inputs["loglevel"][0].data
        return (
            climo,
            resolutions,
            convert_longitudes,
            split_vars,
            split_intervals,
            dry_run,
            operation,
            loglevel,
        )

    def _handler(self, request, response):
        (
            climo,
            resolutions,
            convert_longitudes,
            split_vars,
            split_intervals,
            dry_run,
            operation,
            loglevel,
        ) = self.collect_args(request)

        log_handler(
            self, response, "Starting Process", process_step="start", log_level=loglevel
        )

        filepaths = get_filepaths(request.inputs["netcdf"])
        if dry_run:
            log_handler(self, response, "Dry Run", process_step="dry_run", log_level=loglevel)
            del response.outputs["output"]  # remove unnecessary output
            dry_files = [
                dry_run_info(
                    dry_output_filename(self.workdir, filepath),
                    dry_run_handler,
                    filepath=filepath,
                    climo=climo,
                )
                for filepath in filepaths
            ]

            response.outputs["dry_output"].data = build_meta_link(
                varname="dry_run",
                desc="Dry Run",
                outfiles=dry_files,
                format_name="text",
                fmt=FORMATS.TEXT,
            )

        else:
            del response.outputs["dry_output"]  # remove unnecessary output
            response.update_status("Processing filepaths", 10)
            for filepath in filepaths:
                log_handler(
                    self,
                    response,
                    f"Processing {filepath} into climatologies",
                    process_step="process",
                    log_level=loglevel,
                )

                generate_climos(
                    filepath,
                    self.workdir,
                    operation,
                    climo,
                    convert_longitudes=convert_longitudes,
                    split_vars=split_vars,
                    split_intervals=split_intervals,
                    resolutions=resolutions,
                )

            log_handler(
                self,
                response,
                "Collecting climo files",
                process_step="collect_files",
                log_level=loglevel,
            )

            climo_files = collect_output_files(
                self.get_identifier(operation), self.workdir
            )

            log_handler(
                self,
                response,
                "Building final output",
                process_step="build_output",
                log_level=loglevel,
            )
            response.outputs["output"].data = build_meta_link(
                varname="climo",
                desc="Climatology",
                outfiles=climo_files,
                outdir=self.workdir,
            )

        log_handler(
            self, response, "Process Complete", process_step="complete", log_level=loglevel
        )
        return response
