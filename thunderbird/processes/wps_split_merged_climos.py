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
from thunderbird.utils import (
    MAX_OCCURS,
    get_filepaths,
    build_meta_link,
)
from thunderbird.wps_io import log_level, meta4_output

# Library import
import logging

logger = logging.getLogger("PYWPS")


class SplitMergedClimos(Process):
    def __init__(self):
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
        response.update_status("Starting Process", 0)
        loglevel = request.inputs["loglevel"][0].data
        logger.setLevel(getattr(logging, loglevel))
        filepaths = get_filepaths(request)
        response.update_status("Processing files", 10)
        output_filepaths = []
        for path in filepaths:
            logger.info("")
            logger.info(f"Processing: {path}")
            try:
                input_file = CFDataset(path)
            except Exception as e:
                logger.error(f"{e.__class__.__name__}: {e}")
                raise ProcessError(
                    f"The input file {path} could not be converted to a netcdf dataset"
                )
            else:
                output_filepaths.extend(split_merged_climos(input_file, self.workdir))

        response.update_status("File processing complete", 90)
        response.outputs["output"].data = build_meta_link(
            varname="split_climo",
            desc="Split climatologies",
            outfiles=output_filepaths,
            outdir=self.workdir,
        )

        response.update_status("Process complete", 100)
        return response
