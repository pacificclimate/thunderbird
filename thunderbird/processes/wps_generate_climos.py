from pywps import Process, ComplexInput, ComplexOutput, FORMATS
from pywps.app.Common import Metadata
from pywps.validator.mode import MODE
from netCDF4 import Dataset

import logging
import os


LOGGER = logging.getLogger("PYWPS")


class GenerateClimos(Process):
    def __init__(self):
        inputs = [
            ComplexInput(
                "dataset",
                "NetCDF Dataset",
                abstract="path/to/file.nc",
                supported_formats=[FORMATS.NETCDF],
                min_occurs=1,
                max_occurs=1,
                mode=MODE.STRICT,
            ),
        ]
        outputs = [
            ComplexOutput(
                "output",
                "Metadata",
                as_reference=True,
                supported_formats=[FORMATS.TEXT],
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

    @staticmethod
    def _handler(self, request, response):
        # Update status
        response.update_status("Thunderbird process started.", 0)

        # The actual process
        resource = request.inputs['dataset'][0]
        ds = Dataset(resource.file)
        with open(os.path.join(self.workdir, 'out.txt'), 'w') as file:
            response.outputs['output'].file = file.name
            fp.write(f"URL: {resource.url}\n\n")
            fp.write(f"MIME Type: {resource.data_format.mime_type}\n\n")
            for attr in ds.ncattrs():
                fp.write(f"{attr}: {ds.getncattr(attr)}\n\n")

        # Update status
        response.update_status("Thunderbird process complete.", 100)

        return response
