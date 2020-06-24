# Processor imports
from pywps import (
    Process,
    LiteralInput,
    ComplexInput,
    ComplexOutput,
    FORMATS,
)
from pywps.app.Common import Metadata
from pywps.inout.outputs import MetaLink4, MetaFile
from pywps.app.exceptions import ProcessError

# Tool imports
from nchelpers import CFDataset, standard_climo_periods
from dp.generate_climos import create_climo_files
from thunderbird.utils import (
    is_opendap_url,
    collect_output_files,
    build_meta_link,
    log_handler
)

# Library imports
import logging
import os


logger = logging.getLogger("PYWPS")


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
                max_occurs=1,
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
            LiteralInput(
                "dry_run",
                "Dry Run",
                abstract="Checks file to ensure compatible with process",
                data_type="boolean",
            ),
        ]
        outputs = [
            ComplexOutput(
                "output",
                "Output",
                abstract="Collection of climatoligical files",
                as_reference=True,
                supported_formats=[FORMATS.META4],
            ),
            ComplexOutput(
                "dry_output",
                "Dry Output",
                as_reference=True,
                abstract="File information",
                supported_formats=[FORMATS.TEXT],
            ),
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

    def dry_run_info(self, filepath, climo):
        output = ["Dry Run"]
        output.append(f"File: {filepath}")
        try:
            input_file = CFDataset(filepath)
        except Exception as e:
            output.append(f"{e.__class__.__name__}: {e}")
        else:
            periods = input_file.climo_periods.keys() & climo
            output.append(f"climo_periods: {periods}")
            for attr in "project institution model emissions run".split():
                try:
                    output.append(f"{attr}: {getattr(input_file.metadata, attr)}")
                except Exception as e:
                    output.append(f"{attr}: {e.__class__.__name__}: {e}")
            output.append(f"dependent_varnames: {input_file.dependent_varnames()}")
            for attr in "time_resolution is_multi_year_mean".split():
                output.append(f"{attr}: {getattr(input_file, attr)}")

        filename = os.path.join(self.workdir, "dry.txt")
        with open(filename, "w") as f:
            for line in output:
                f.write(f"{line}\n")

        return filename

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
        return (
            climo,
            resolutions,
            convert_longitudes,
            split_vars,
            split_intervals,
            dry_run,
            operation,
        )

    def get_filepath(self, request):
        path = request.inputs["netcdf"][0]
        if is_opendap_url(path.url):
            return path.url
        elif path.file.endswith(".nc"):
            return path.file
        else:
            raise ProcessError(
                "You must provide a data source (opendap/netcdf). "
                f"Inputs provided: {request.inputs}"
            )

    def _handler(self, request, response):
        log_handler(self, response, "Starting Process", process_step="start")

        (
            climo,
            resolutions,
            convert_longitudes,
            split_vars,
            split_intervals,
            dry_run,
            operation,
        ) = self.collect_args(request)
        filepath = self.get_filepath(request)

        if dry_run:
            log_handler(self, response, "Dry Run", process_step="dry_run")
            del response.outputs["output"]  # remove unnecessary output
            response.outputs["dry_output"].file = self.dry_run_info(filepath, climo)

        else:
            del response.outputs["dry_output"]  # remove unnecessary output
            input_file = CFDataset(filepath)

            periods = [period for period in input_file.climo_periods.keys() & climo]

            log_handler(self, response, f"Processing {filepath} into climatologies", process_step="process")

            for period in periods:
                t_range = input_file.climo_periods[period]
                create_climo_files(
                    period,
                    self.workdir,
                    input_file,
                    operation,
                    *t_range,
                    convert_longitudes=convert_longitudes,
                    split_vars=split_vars,
                    output_resolutions=resolutions,
                )

            log_handler(self, response, "Collecting climo files", process_step="collect_files")

            climo_files = collect_output_files(
                self.get_identifier(operation), self.workdir
            )

            log_handler(self, response, "Building final output", process_step="build_output")
            response.outputs["output"].data = build_meta_link(
                "climo", "Climatology", climo_files, self.workdir
            )

        log_handler(self, response, "Process Complete", process_step="complete")
        return response
