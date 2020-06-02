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
from requests.exceptions import ConnectionError, InvalidSchema, MissingSchema

# Tool imports
from nchelpers import CFDataset
from dp.generate_prsn import generate_prsn_file
from dp.generate_prsn import dry_run as dry_run_info
import dp

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
                abstract="Optional custom name of output file",
                data_type="string",
            ),
            LiteralInput(
                "loglevel",
                "Log Level",
                default="INFO",
                abstract="Logging level",
                allowed_values=["INFO", "DEBUG", "WARNING", "ERROR"],
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
                abstract="Precipitation as snow file",
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

        super(GeneratePrsn, self).__init__(
            self._handler,
            identifier="generate_prsn",
            #version=?
            title="Generate Precipitation as Snow",
            abstract="Generate Precipitation as Snow",
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
            filepaths[var] = path.data
        return filepaths
   
    def setup_logger(self, level):
        formatter = logging.Formatter("%(asctime)s %(levelname)s: %(message)s",
                                      "%Y-%m-%d %H:%M:%S")
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(level)

    def collect_prsn_file(self):
        return [file for file in os.listdir(self.workdir) if file.endswith(".nc")][0]

    def build_meta_link(self, prsn_file):
        meta_link = MetaLink4(
            "output", "Output of netCDF prsn file", workdir=self.workdir
        )

        # Create a MetaFile instance, which instantiates a ComplexOutput object.
        meta_file = MetaFile(f"{prsn_file}", "Precipitation as snow", fmt=FORMATS.NETCDF)
        meta_file.file = os.path.join(self.workdir, prsn_file)
        meta_link.append(meta_file)

        return meta_link.xml

    def _handler(self, request, response):
        response.update_status("Starting Process", 0)

        (
            chunk_size,
            loglevel,
            dry_run,
            output_file
        ) = self.collect_args(request)
        filepaths = self.get_filepaths(request)
        self.setup_logger(loglevel)

        if dry_run:
            response.update_status("Dry Run", 10)
            del response.outputs["output"]  # remove unnecessary output
            response.outputs["dry_output"].file = dry_run_info(
                filepaths, output_to_file=True, workdir=self.workdir
            )

        else:
            del response.outputs["dry_output"] # remove unnecessary output

            response.update_status("Processing files", 10)
            generate_prsn_file(filepaths, chunk_size, self.workdir, output_file)

            response.update_status("File processing complete", 90)
            prsn_file = self.collect_prsn_file()

            response.update_status("Collecting output file", 95)
            response.outputs["output"].data = self.build_meta_link(prsn_file)

        response.update_status("Process complete", 100)
        return response
            
