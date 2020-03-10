# Processor imports
from pywps import (
    Process,
    LiteralInput,
    ComplexInput,
    LiteralOutput,
    ComplexOutput,
    FORMATS,
)
from pywps.app.Common import Metadata
from pywps.inout.outputs import MetaLink, MetaLink4, MetaFile
from pywps.inout.literaltypes import AllowedValue
from pywps.validator.mode import MODE

# Tool imports
from nchelpers import CFDataset
from dp.generate_climos import create_climo_files

# Library imports
import logging
import os

# Local imports
from .utils.loading_bar import LoadingBar


LOGGER = logging.getLogger("PYWPS")


class GenerateClimos(Process):
    def __init__(self):
        self.climos = {'historical': ['6190', '7100', '8100'], 'futures': ['2020', '2050', '2080']}
        self.resolutions = ["all", "yearly", "seasonal", "monthy",]

        inputs = [
            ComplexInput(
                "dataset",
                "Daily NetCDF Dataset",
                abstract="Path to OPEnDAP resource",
                min_occurs=1,
                max_occurs=1,
                supported_formats=[FORMATS.DODS],
            ),
            LiteralInput(
                "operation",
                "Data Operation",
                abstract="Operation to perform on the datasets",
                allowed_values=["mean", "std",],
                data_type="string",
            ),
            LiteralInput(
                "climo",
                "Climatological Period",
                abstract="Year ranges",
                min_occurs=1,
                max_occurs=6,
                mode=0,
                allowed_values=["all"] + [key for key in self.climos.keys()] + [item for value in self.climos.values() for item in value],
                data_type="string",
            ),
            LiteralInput(
                "resolutions",
                "Temporal Resolutions",
                min_occurs=1,
                max_occurs=3,
                allowed_values=self.resolutions,
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
                abstract="Generate a separate file for each dependent variable in the file",
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
                supported_formats=[FORMATS.TEXT]
            ),
        ]

        super(GenerateClimos, self).__init__(
            self._handler,
            identifier="generate_climos",
            version="0.8.0",
            title="Generate Climatological Means",
            abstract="Generate files containing climatological means from input files of daily, monthly, or yearly data that adhere to the PCIC metadata standard (and consequently to CMIP5 and CF standards).",
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

        filename = os.path.join(self.workdir, 'dry.txt')
        with open(filename, 'w') as f:
            for line in output:
                f.write(f'{line}\n')

        return filename

    def collect_climo_files(self):
        return [file for file in os.listdir(self.workdir) if file.endswith('.nc')]

    def build_meta_link(self, climo_files):
        meta_link = MetaLink4(
            "outputs", "Output of netCDF climo files", workdir=self.workdir
        )

        for file in climo_files:
            # Create a MetaFile instance, which instantiates a ComplexOutput object.
            meta_file = MetaFile(f'{file}', 'Climatology', fmt=FORMATS.NETCDF)
            meta_file.file = os.path.join(self.workdir, file)
            meta_link.append(meta_file)

        return meta_link.xml

    def format_climo(self, climo):
        if 'all' in climo:
            return self.climos['historical'] + self.climos['futures']

        # loop over given climo, replace items ('historical', 'futures') with
        # items from list
        return list(set([item for c in climo for item in (self.climos[c] if c in self.climos.keys() else [c])]))

    def format_resolutions(self, resolutions):
        if 'all' in resolutions:
            return [resolution for resolution in self.resolutions if resolution != 'all']

        return list(set(resolutions))

    def collect_args(self, request):
        climo = self.format_climo([climo.data for climo in request.inputs["climo"]])
        operation = request.inputs["operation"][0].data
        resolutions = self.format_resolutions([resolution.data for resolution in request.inputs["resolutions"]])
        convert_longitudes = request.inputs["convert_longitudes"][0].data
        split_vars = request.inputs["split_vars"][0].data
        split_intervals = request.inputs["split_intervals"][0].data
        dry_run = request.inputs["dry_run"][0].data
        return climo, resolutions, convert_longitudes, split_vars, split_intervals, dry_run, operation

    def _handler(self, request, response):
        loading_bar = LoadingBar(response, start=0, end=5, num_processes=1)
        loading_bar.begin()

        climo, resolutions, convert_longitudes, split_vars, split_intervals, dry_run, operation = self.collect_args(request)
        resource = request.inputs["dataset"][0]
        filepath = resource.url

        loading_bar.update_status('Collected Variables')

        if dry_run:
            del response.outputs['output']  # remove unnecessary output
            loading_bar.update_range(end=99, num_processes=1)
            loading_bar.begin('Starting Dry Run')
            response.outputs["dry_output"].file = self.dry_run_info(filepath, climo)

        else:
            del response.outputs['dry_output']  # remove unnecessary output
            input_file = CFDataset(filepath)

            periods = [period for period in input_file.climo_periods.keys() & climo]
            loading_bar.update_range(end=99, num_processes=(len(periods)*2) + 1)
            loading_bar.begin(f'Processing {filepath}')

            for period in periods:
                loading_bar.update_status(f'Processing period: {period}')

                t_range = input_file.climo_periods[period]
                create_climo_files(
                    self.workdir,
                    input_file,
                    operation,
                    *t_range,
                    convert_longitudes=convert_longitudes,
                    split_vars=split_vars,
                    output_resolutions=resolutions,
                )

                loading_bar.update_status("Climo file created")

            climo_files = self.collect_climo_files()

            loading_bar.update_status('Collecting output files')
            response.outputs["output"].data = self.build_meta_link(climo_files)

        loading_bar.finish_process()
        return response
