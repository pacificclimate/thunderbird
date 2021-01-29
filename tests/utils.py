import io
import pytest
from pkg_resources import resource_listdir
from contextlib import redirect_stderr

from wps_tools.testing import run_wps_process


TESTDATA = {
    "test_local_nc": [
        test_file
        for test_file in resource_listdir(__name__, "data")
        if test_file.endswith(".nc")
    ],
    "test_opendaps": [
        "pr_day_BCCAQv2%2BANUSPLIN300_NorESM1-M_historical%2Brcp26_r1i1p1_19500101-19500107.nc",
        "tasmin_day_BCCAQv2%2BANUSPLIN300_NorESM1-M_historical%2Brcp26_r1i1p1_19500101-19500107.nc",
        "tasmax_day_BCCAQv2%2BANUSPLIN300_NorESM1-M_historical%2Brcp26_r1i1p1_19500101-19500107.nc",
        "tiny_gcm_climos.nc",
        "tiny_gcm_360_climos.nc",
        "tiny_downscaled_tasmax_climos.nc",
        "gdd_annual_CanESM2_rcp85_r1i1p1_1951-2100.nc",
        "fdd_seasonal_CanESM2_rcp85_r1i1p1_1951-2100.nc",
        "sample_flow_parameters.nc",
    ],
}
