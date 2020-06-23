from pywps import LiteralInput, ComplexInput, ComplexOutput, FORMATS

import logging


def ncInput(identifier, title, abstract, max_occurs):
    return ComplexInput(
        identifier,
        title,
        abstract=abstract,
        min_occurs=1,
        max_occurs=max_occurs,
        supported_formats=[FORMATS.NETCDF, FORMATS.DODS],
    )


def loglevel_input():
    return LiteralInput(
        "loglevel",
        "Log Level",
        default="INFO",
        abstract="Logging level",
        allowed_values=list(logging._levelToName.values()),
    )


def dryrun_input():
    return LiteralInput(
        "dry_run",
        "Dry Run",
        abstract="Checks file to ensure compatible with process",
        data_type="boolean",
    )


def outFiles(abstract, formats):
    return ComplexOutput(
        "output",
        "Output",
        abstract=abstract,
        as_reference=True,
        supported_formats=formats,
    )


def dryrun_output():
    return ComplexOutput(
        "dry_output",
        "Dry Output",
        as_reference=True,
        abstract="File information",
        supported_formats=[FORMATS.TEXT],
    )
