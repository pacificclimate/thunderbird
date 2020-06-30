from pywps import LiteralInput, ComplexOutput, FORMATS

import logging

log_level = LiteralInput(
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


meta4_output = ComplexOutput(
    "output",
    "Output",
    as_reference=True,
    abstract="Metalink object between output files",
    supported_formats=[FORMATS.META4],
)

nc_output = ComplexOutput(
    "output",
    "Output",
    as_reference=True,
    abstract="Output Netcdf File",
    supported_formats=[FORMATS.NETCDF],
)

dryrun_output = ComplexOutput(
    "dry_output",
    "Dry Output",
    as_reference=True,
    abstract="File information",
    supported_formats=[FORMATS.TEXT],
)

meta4_dryrun_output = ComplexOutput(
    "dry_output",
    "Dry Output",
    as_reference=True,
    abstract="Metalink object between dry output files",
    supported_formats=[FORMATS.META4],
)
