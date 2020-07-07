# Processor imports
from pywps import FORMATS
from requests import head
from requests.exceptions import ConnectionError, MissingSchema, InvalidSchema
from pywps.inout.outputs import MetaLink4, MetaFile
from pywps.app.exceptions import ProcessError

# Tool import
from nchelpers import CFDataset

# Library imports
import logging
import os

MAX_OCCURS = 1000


pywps_logger = logging.getLogger("PYWPS")
stderr_logger = logging.getLogger(__name__)

formatter = logging.Formatter(
    "%(asctime)s %(levelname)s: thunderbird: %(message)s", "%Y-%m-%d %H:%M:%S"
)
handler = logging.StreamHandler()
handler.setFormatter(formatter)
stderr_logger.addHandler(handler)
stderr_logger.setLevel(stderr_logger.level)


def is_opendap_url(url):  # From Finch bird
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
        content_description = head(url, timeout=5).headers.get("Content-Description")
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


def get_filepaths(request):
    filepaths = []
    for path in request.inputs["netcdf"]:
        if is_opendap_url(path.url):
            filepaths.append(path.url)
        elif path.file.endswith(".nc"):
            filepaths.append(path.file)
        else:
            raise ProcessError(
                "You must provide a data source (opendap/netcdf). "
                f"Inputs provided: {request.inputs}"
            )
    return filepaths


def collect_output_files(varname, outdir=os.getcwd()):
    """
    Collect output netcdf files.

    Parameters:
        varname (str): name of variable (must be in filenames)
        outdir (str): Directory containing output files
    """
    return [file for file in os.listdir(outdir) if varname in file]


def build_meta_link(
    varname,
    desc,
    outfiles,
    format_name="netCDF",
    fmt=FORMATS.NETCDF,
    outdir=os.getcwd(),
):
    """
    Create meta link between output netcdf files.

    Parameters:
        varname (str): name of variable (used for MetaLink4)
        desc (str): Description of meta file
        outfiles (list): List of output files
        format_name (str): Format name of output files
        fmt (FORMATS): Format of output files
        outdir (str): Directory containing output files
    """
    if len(outfiles) == 1:
        meta_link = MetaLink4(
            "output", f"Output of {format_name} {varname} file", workdir=outdir
        )
    else:
        meta_link = MetaLink4(
            "output", f"Output of {format_name} {varname} files", workdir=outdir
        )

    for file in outfiles:
        # Create a MetaFile instance, which instantiates a ComplexOutput object.
        meta_file = MetaFile(f"{file}", desc, fmt=fmt)
        meta_file.file = os.path.join(outdir, file)
        meta_link.append(meta_file)

    return meta_link.xml


def log_handler(process, response, message, process_step=None, level="INFO"):
    if process_step:
        status_percentage = process.status_percentage_steps[process_step]
    else:
        status_percentage = response.status_percentage

    # Log to all sources
    pywps_logger.log(getattr(logging, level), message)
    stderr_logger.log(getattr(logging, level), message)
    response.update_status(message, status_percentage=status_percentage)
