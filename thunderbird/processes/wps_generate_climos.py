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


LOGGER = logging.getLogger("PYWPS")


class GenerateClimos(Process):
    def __init__(self):
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
                allowed_values=["6190", "7100", "8100", "2020", "2050", "2080",],
                data_type="string",
            ),
            LiteralInput(
                "resolutions",
                "Temporal Resolutions",
                min_occurs=1,
                max_occurs=3,
                allowed_values=["yearly", "seasonal", "monthy",],
                data_type="string",
            ),
            LiteralInput(
                "dry_run",
                "Dry Run",
                abstract="Opt-in dry run on file set",
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
            LiteralOutput(
                "dry_output",
                "Dry Output",
                abstract="File information",
                data_type="string",
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
        report = "Dry Run\n"
        report += f"File: {filepath}\n"
        try:
            input_file = CFDataset(filepath)
        except Exception as e:
            report += f"{e.__class__.__name__}: {e}\n"
        else:
            periods = input_file.climo_periods.keys() & climo
            report += f"climo_periods: {periods}\n"
            for attr in "project institution model emissions run".split():
                try:
                    report += f"{attr}: {getattr(input_file.metadata, attr)}\n"
                except Exception as e:
                    report += f"{attr}: {e.__class__.__name__}: {e}\n"
            report += f"dependent_varnames: {input_file.dependent_varnames()}\n"
            for attr in "time_resolution is_multi_year_mean".split():
                report += f"{attr}: {getattr(input_file, attr)}\n"
        return report

    def _handler(self, request, response):
        response.update_status("Process started.", 0)

        # set up from args
        climo = [climo.data for climo in request.inputs["climo"]]
        resolutions = [resolution.data for resolution in request.inputs["resolutions"]]
        dry_run = request.inputs["dry_run"][0].data
        operation = request.inputs["operation"][0].data

        # todel
        print(f"CLIMO: {climo}")
        print(f"RESOLUTIONS: {resolutions}")
        print(f"OPERATION: {operation}")

        # set up data items
        resource = request.inputs["dataset"][0]
        filepath = resource.url

        if dry_run:
            response.outputs["dry_output"].data = self.dry_run_info(filepath, climo)
        else:
            print(f"Processing: {filepath}")
            input_file = CFDataset(filepath)
            for period in input_file.climo_periods.keys() & climo:
                t_range = input_file.climo_periods[period]
                create_climo_files(
                    self.workdir,
                    input_file,
                    operation,
                    *t_range,
                    convert_longitudes=False,
                    split_vars=False,
                    output_resolutions=resolutions,
                )

            expected_files = [
                "tasmin_aClimMean_BCCAQv2_inmcm4_historical+rcp85_r1i1p1_19610101-19901231_Canada.nc",
                "tasmin_sClimMean_BCCAQv2_inmcm4_historical+rcp85_r1i1p1_19610101-19901231_Canada.nc",
                "tasmin_mClimMean_BCCAQv2_inmcm4_historical+rcp85_r1i1p1_19610101-19901231_Canada.nc",
            ]

            # Create metalink bundle for output
            meta_link = MetaLink4(
                "outputs", "Output of netCDF climo files", workdir=self.workdir
            )

            for file in expected_files:
                # Create a MetaFile instance, which instantiates a ComplexOutput object.
                meta_file = MetaFile(f'{file}', 'Climatology', fmt=FORMATS.NETCDF)
                meta_file.file = os.path.join(self.workdir, file)
                meta_link.append(meta_file)

            response.outputs["output"].data = meta_link.xml

        response.update_status("Process completed.", 100)
        return response
