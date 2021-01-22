# wps_split_merged_climos

#### wps_split_merged_climos is a process that runs the [split_merged_climos](https://github.com/pacificclimate/climate-explorer-data-prep#split_merged_climos-split-climo-means-files-into-per-interval-files-month-season-year) module of PCIC Climate Explorer Data Preparation Tools. Here, the client will try to connect to a remote Thunderbird instance using the url parameter.


```python
from birdy import WPSClient
from pkg_resources import resource_filename
import requests
import os
from bs4 import BeautifulSoup
from wps_tools.testing import get_target_url
from wps_tools.output_handling import get_metalink_content

# Ensure we are in the working directory with access to the data
while os.path.basename(os.getcwd()) != "thunderbird":
    os.chdir('../')
```


```python
# NBVAL_IGNORE_OUTPUT
url = get_target_url("thunderbird")
print(f"Using thunderbird on {url}")
```

    Using thunderbird on https://docker-dev03.pcic.uvic.ca/twitcher/ows/proxy/thunderbird/wps



```python
thunderbird = WPSClient(url)
```

#### Help for individual processes can be diplayed using the ? command (ex. bird.process?).


```python
# NBVAL_IGNORE_OUTPUT
thunderbird.split_merged_climos?
```


    [0;31mSignature:[0m [0mthunderbird[0m[0;34m.[0m[0msplit_merged_climos[0m[0;34m([0m[0mnetcdf[0m[0;34m=[0m[0;32mNone[0m[0;34m,[0m [0mloglevel[0m[0;34m=[0m[0;34m'INFO'[0m[0;34m)[0m[0;34m[0m[0;34m[0m[0m
    [0;31mDocstring:[0m
    Split climo means files into one file per time interval
    
    Parameters
    ----------
    netcdf : ComplexData:mimetype:`application/x-netcdf`, :mimetype:`application/x-ogc-dods`
        NetCDF files to process
    loglevel : {'CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'NOTSET'}string
        Logging level
    
    Returns
    -------
    output : ComplexData:mimetype:`application/metalink+xml; version=4.0`
        Metalink object between output files
    [0;31mFile:[0m      ~/code/birds/thunderbird/</tmp/thunderbird-venv/lib/python3.8/site-packages/birdy/client/base.py-3>
    [0;31mType:[0m      method



#### We can use the docstring to ensure we provide the appropriate parameters.


```python
# Test local and opendap files
tasmax_climos_local = resource_filename('tests', 'data/tiny_downscaled_tasmax_climos.nc')
hydromodel_climos_opendap = "https://docker-dev03.pcic.uvic.ca/twitcher/ows/proxy/thredds/dodsC/datasets/storage/data/projects/comp_support/daccs/test-data/tiny_hydromodel_gcm_climos.nc"
multiple_inputs = [tasmax_climos_local, hydromodel_climos_opendap]

output = thunderbird.split_merged_climos(multiple_inputs)
```


```python
split_filepaths = get_metalink_content(output.get()[0])
```

#### Once the process has completed we can extract the results and ensure it is what we expected.


```python
# Check number of output files
assert len(split_filepaths) == len(multiple_inputs) * 3     # 3 output files (aClim, sClim and mClim) for each input file

# Check number of output files corresponding to each interval
aClims = [sf for sf in split_filepaths if 'aClim' in sf]    # annual
sClims = [sf for sf in split_filepaths if 'sClim' in sf]    # seasonal
mClims = [sf for sf in split_filepaths if 'mClim' in sf]    # monthly

assert len(aClims) == len(multiple_inputs)
assert len(sClims) == len(multiple_inputs)
assert len(mClims) == len(multiple_inputs)
```
