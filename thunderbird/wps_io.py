from pywps import LiteralInput, ComplexOutput, FORMATS

import logging

loglevel = LiteralInput(
    "loglevel",
    "Log Level",
    default="INFO",
    abstract="Logging level",
    allowed_values=list(logging._levelToName.values()),
)


dryrun_input = LiteralInput(
    "dry_run",
    "Dry Run",
    abstract="Checks file to ensure compatible with process",
    data_type="boolean",
)


meta4Output = ComplexOutput(
    "output",
    "Output",
    as_reference=True,
    abstract="Metalink object between output files",
    supported_formats=[FORMATS.META4],
)

ncOutput = ComplexOutput(
    "output",
    "Output",
    as_reference=True,
    abstract="Output Netcdf Files",
    supported_formats=[FORMATS.NETCDF],
)

dryrun_output = ComplexOutput(
    "dry_output",
    "Dry Output",
    as_reference=True,
    abstract="File information",
    supported_formats=[FORMATS.TEXT],
)
