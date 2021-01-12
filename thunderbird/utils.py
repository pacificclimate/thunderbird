# Library imports
import logging
import os

logger = logging.getLogger("PYWPS")
logger.setLevel(logging.NOTSET)

formatter = logging.Formatter(
    "%(asctime)s %(levelname)s: thunderbird: %(message)s", "%Y-%m-%d %H:%M:%S"
)
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger.addHandler(handler)


def dry_run_info(filename, dry_run_method, **kwargs):
    """
    This function creates an output file with the given filename.
    logging.basicConfig() is used to redirect messages logged from
    dry_run_method to the created file. After dry_run is processed,
    logging.root.removeHandler(handler) resets logging configuration
    to redirect further logging messages to terminal.
    """
    with open(filename, "w") as f:
        f.write("Dry Run\n")
        logging.basicConfig(filename=filename, level=logging.INFO)
        dry_run_method(**kwargs)
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)

    return filename


def dry_output_filename(outdir, filename):
    if filename.endswith(".nc"):
        return os.path.join(
            outdir, os.path.basename(filename).split(".")[0] + "_dry.txt",
        )
    else:
        return os.path.join(outdir, filename)


def get_url():
    """Determine which url to target for notebooks

    "DEV" and "LOCAL" urls may be targeted by the Makefile testing procedures.
    If neither of those environment variables are set, the default docker url will be used.
    """
    for url in [os.getenv("DEV_URL"), os.getenv("LOCAL_URL")]:
        if url:
            return url

    return "https://docker-dev03.pcic.uvic.ca/twitcher/ows/proxy/thunderbird/wps"


#######################################
from wps_tools.output_handling import (
    rda_to_vector,
    get_robjects,
    nc_to_dataset,
    json_to_dict,
    txt_to_string,
)
import requests
from bs4 import BeautifulSoup


def auto_construct_outputs(outputs):
    """
    Automatically construct Python objects from input url files.
    Written to construct complex WPS process Outputs.
    Parameters:
        outputs (list): list of file or http url paths to files
    Returns:
        list: the constructed python objects in a list
    """
    process_outputs = []
    for value in outputs:
        if value.endswith(".rda") or value.endswith(".rdata"):
            output = [rda_to_vector(value, obj) for obj in get_robjects(value)]

        elif value.endswith(".nc"):
            output = nc_to_dataset(value)

        elif value.endswith(".json"):
            output = json_to_dict(value)

        elif value.endswith(".txt"):
            output = txt_to_string(value)

        elif value.endswith(".meta4"):
            req = requests.get(value)
            metalinks = BeautifulSoup(
                BeautifulSoup(req.content.decode("utf-8"), features="lxml").prettify(),
                features="lxml",
            ).find_all("metaurl")

            return auto_construct_outputs(
                [
                    metalink.get_text().replace("\n", "").replace(" ", "")
                    for metalink in metalinks
                ]
            )

        else:
            output = value

        process_outputs.extend(output if type(output) == list else [output])

    return process_outputs
