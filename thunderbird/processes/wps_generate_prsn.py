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
from requests import head
from requests.exceptions import ConnectionError, MissingSchema, InvalidSchema

# Tool imports
from nchelpers import CFDataset
from dp.generate_prsn import generate_prsn_file
#from dp.generate_prsn import dry_run as dry_run_info
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
                default="None",
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
            title="Generate Precipitation as Snow",
            abstract="Generate precipitation as snow file from precipitation, and minimum/maximum temperature data",
            metadata=[
                Metadata("NetCDF processing"),
                Metadata("Climate Data Operations"),
            ],
            inputs=inputs,
            outputs=outputs,
            store_supported=True,
            status_supported=True,
        )

    def dry_run_info(self, filepaths, output_to_file=False, workdir=None):
        '''Perform metadata checks on the input files'''
        if output_to_file: # Used for wps process in thunderbird
            output = ['Dry Run']
            for filepath in filepaths.values():
                output.append('File: {}'.format(filepath))
                try:
                    dataset = CFDataset(filepath)
                except Exception as e:
                    output.append('{}: {}'.format(e.__class__.__name__, e))

                for attr in 'project model institute experiment ensemble_member'.split():
                    try:
                        output.append('{}: {}'.format(attr, getattr(dataset.metadata, attr)))
                    except Exception as e:
                        output.append('{}: {}: {}'.format(attr, e.__class__.__name__, e))
                output.append('dependent_varnames: {}'.format(dataset.dependent_varnames()))

            filename = os.path.join(workdir, 'dry.txt')
            with open(filename, 'w') as f:
                for line in output:
                    f.write('{}\n'.format(line))

            return filename

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

    def is_opendap_url(self, url): # From Finch bird
        """
        Check if a provided url is an OpenDAP url.
        The DAP Standard specifies that a specific tag must be included in the
        Content-Description header of every request. This tag is one of:
            "dods-dds" | "dods-das" | "dods-data" | "dods-error"
        So we can check if the header starts with `dods`.
        Even then, some OpenDAP servers seem to not include the specified header...
        So we need to let the netCDF4 library actually open the file.
       """
        try:
            content_description = head(url, timeout=5).headers.get(
                "Content-Description"
            )
        except (ConnectionError, MissingSchema, InvalidSchema):
            return False

        if content_description:
            return content_description.lower().startswith("dods")
        else:
            try:
                dataset = CFDataset(url)
            except OSError:
                return False
            return dataset.disk_format in ("DAP2", "DAP4")

    def get_filepaths(self, request):
        filepaths = {}
        var_list = ["pr", "tasmin", "tasmax"]
        data_files = [
            request.inputs["prec"][0],
            request.inputs["tasmin"][0],
            request.inputs["tasmax"][0],
        ]
        for var, path in zip(var_list, data_files):
            if self.is_opendap_url(path.url):
                filepaths[var] = path.url
            else:
                filepaths[var] = path.file
        return filepaths
   
    def setup_logger(self, level):
        formatter = logging.Formatter("%(asctime)s %(levelname)s: %(message)s",
                                      "%Y-%m-%d %H:%M:%S")
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(level)

    def collect_prsn_file(self):
        return [file for file in os.listdir(self.workdir) if "prsn" in file][0]

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
        output_file = None if output_file == "None" else output_file
        filepaths = self.get_filepaths(request)
        filepaths["pr"] = filepaths["pr"].replace(" ", "+")
        filepaths["tasmin"] = filepaths["tasmin"].replace(" ", "+")
        filepaths["tasmax"] = filepaths["tasmax"].replace(" ", "+")
        self.setup_logger(loglevel)

        if dry_run:
            response.update_status("Dry Run", 10)
            del response.outputs["output"]  # remove unnecessary output
            # dry_output_path = os.path.join(self.workdir, 'dry.txt')
            # dry_run_info(filepaths, dry_output_path)
            # response.outputs["dry_output"].file = dry_output_path
            response.outputs["dry_output"].file = self.dry_run_info(
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
            
