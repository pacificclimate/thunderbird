## Generate Climos

This process runs [generate_climos](https://github.com/pacificclimate/climate-explorer-data-prep/blob/master/README.md#generate_climos-generate-climatological-means), which creates files with climatological means/standard deviations of input data from a netcdf file.


```python
from birdy import WPSClient
import requests
import os
from urllib.request import urlopen, urlretrieve
from netCDF4 import Dataset
from tempfile import NamedTemporaryFile
from bs4 import BeautifulSoup
import re
from wps_tools.testing import get_target_url
from wps_tools.output_handling import auto_construct_outputs, txt_to_string, get_metalink_content, nc_to_dataset
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


```python
# NBVAL_IGNORE_OUTPUT
# Check info on `generate_climos` process
thunderbird.generate_climos?
```


    [0;31mSignature:[0m
    [0mthunderbird[0m[0;34m.[0m[0mgenerate_climos[0m[0;34m([0m[0;34m[0m
    [0;34m[0m    [0mnetcdf[0m[0;34m,[0m[0;34m[0m
    [0;34m[0m    [0moperation[0m[0;34m,[0m[0;34m[0m
    [0;34m[0m    [0mdry_run[0m[0;34m=[0m[0;32mNone[0m[0;34m,[0m[0;34m[0m
    [0;34m[0m    [0mconvert_longitudes[0m[0;34m=[0m[0;32mTrue[0m[0;34m,[0m[0;34m[0m
    [0;34m[0m    [0msplit_vars[0m[0;34m=[0m[0;32mTrue[0m[0;34m,[0m[0;34m[0m
    [0;34m[0m    [0msplit_intervals[0m[0;34m=[0m[0;32mTrue[0m[0;34m,[0m[0;34m[0m
    [0;34m[0m    [0mloglevel[0m[0;34m=[0m[0;34m'INFO'[0m[0;34m,[0m[0;34m[0m
    [0;34m[0m    [0mclimo[0m[0;34m=[0m[0;32mNone[0m[0;34m,[0m[0;34m[0m
    [0;34m[0m    [0mresolutions[0m[0;34m=[0m[0;32mNone[0m[0;34m,[0m[0;34m[0m
    [0;34m[0m[0;34m)[0m[0;34m[0m[0;34m[0m[0m
    [0;31mDocstring:[0m
    Generate files containing climatological means from input files of daily, monthly, or yearly data that adhere to the PCIC metadata standard (and consequently to CMIP5 and CF standards).
    
    Parameters
    ----------
    netcdf : ComplexData:mimetype:`application/x-netcdf`, :mimetype:`application/x-ogc-dods`
        NetCDF file
    operation : {'mean', 'std'}string
        Operation to perform on the datasets
    climo : {'6190', '7100', '8110', '2020', '2050', '2080'}string
        Year ranges
    resolutions : {'all', 'yearly', 'seasonal', 'monthly'}string
        Temporal Resolutions
    convert_longitudes : boolean
        Transform longitude range from [0, 360) to [-180, 180)
    split_vars : boolean
        Generate a separate file for each dependent variable in the file
    split_intervals : boolean
        Generate a separate file for each climatological period
    dry_run : boolean
        Checks file to ensure compatible with process
    loglevel : {'CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'NOTSET'}string
        Logging level
    
    Returns
    -------
    output : ComplexData:mimetype:`application/metalink+xml; version=4.0`
        Metalink object between output files
    dry_output : ComplexData:mimetype:`application/metalink+xml; version=4.0`
        Metalink object between dry output files
    [0;31mFile:[0m      ~/code/birds/thunderbird/docs/source/notebooks/</tmp/thunderbird-venv/lib/python3.8/site-packages/birdy/client/base.py-0>
    [0;31mType:[0m      method



## Single File run
**Dry Run -** Checks file to ensure compatible with process


```python
# Set up variables for thunderbird.generate_climos
seasonal_opendap = 'https://docker-dev03.pcic.uvic.ca/twitcher/ows/proxy/thredds/dodsC/datasets/storage/data/projects/comp_support/daccs/test-data/fdd_seasonal_CanESM2_rcp85_r1i1p1_1951-2100.nc'
annual_opendap = 'https://docker-dev03.pcic.uvic.ca/twitcher/ows/proxy/thredds/dodsC/datasets/storage/data/projects/comp_support/daccs/test-data/gdd_annual_CanESM2_rcp85_r1i1p1_1951-2100.nc'
operation = 'mean'
climo = '6190'
resolutions = 'yearly'
dry_run = True

# Dry run process
dry_output = thunderbird.generate_climos(
    netcdf=seasonal_opendap, 
    operation=operation, 
    climo=climo, 
    resolutions=resolutions, 
    dry_run=dry_run
)
dry_output.get()[0]
```




    'http://localhost:5000/outputs/8b3dcce2-545a-11eb-9bea-9bfa3f22d465/input.meta4'



Access the output with **auto_construct_outputs()** or **get_metalink_content()** with **txt_to_string()** from wps_tools.output_handling


```python
# NBVAL_IGNORE_OUTPUT
auto_construct_outputs(dry_output.get())
```




    ["Dry Run\ngenerate_climos:\nINFO:dp.generate_climos:Processing: https://docker-dev03.pcic.uvic.ca/twitcher/ows/proxy/thredds/dodsC/datasets/storage/data/projects/comp_support/daccs/test-data/fdd_seasonal_CanESM2_rcp85_r1i1p1_1951-2100.nc\nINFO:dp.generate_climos:climo_periods: {'6190'}\nINFO:dp.generate_climos:project: CMIP5\nINFO:dp.generate_climos:institution: PCIC\nINFO:dp.generate_climos:model: CanESM2\nINFO:dp.generate_climos:emissions: historical, rcp85\nINFO:dp.generate_climos:run: r1i1p1\nINFO:dp.generate_climos:dependent_varnames: ['fdd']\nINFO:dp.generate_climos:time_resolution: seasonal\nINFO:dp.generate_climos:is_multi_year_mean: False\n"]




```python
# NBVAL_IGNORE_OUTPUT
meta_content = get_metalink_content(dry_output.get()[0])
print(meta_content)
txt_content = txt_to_string(meta_content[0])
print(txt_content)
```

    ['http://localhost:5000/outputs/8b3dcce3-545a-11eb-9bea-9bfa3f22d465/fdd_seasonal_CanESM2_rcp85_r1i1p1_1951-2100_dry.txt']
    Dry Run
    generate_climos:
    INFO:dp.generate_climos:Processing: https://docker-dev03.pcic.uvic.ca/twitcher/ows/proxy/thredds/dodsC/datasets/storage/data/projects/comp_support/daccs/test-data/fdd_seasonal_CanESM2_rcp85_r1i1p1_1951-2100.nc
    INFO:dp.generate_climos:climo_periods: {'6190'}
    INFO:dp.generate_climos:project: CMIP5
    INFO:dp.generate_climos:institution: PCIC
    INFO:dp.generate_climos:model: CanESM2
    INFO:dp.generate_climos:emissions: historical, rcp85
    INFO:dp.generate_climos:run: r1i1p1
    INFO:dp.generate_climos:dependent_varnames: ['fdd']
    INFO:dp.generate_climos:time_resolution: seasonal
    INFO:dp.generate_climos:is_multi_year_mean: False
    



```python
expected_items = ['6190', 'CMIP5', 'PCIC', 'CanESM2', 'historical', 'rcp85', 'r1i1p1', 'fdd', 'seasonal']
for item in expected_items:
    assert item in txt_content
```

**Normal Run**


```python
# generate climos
output = thunderbird.generate_climos(
    netcdf=seasonal_opendap, 
    operation=operation, 
    climo=climo, 
    resolutions=resolutions, 
    dry_run=False
)
```


```python
""" Helper function to test netCDF file output -
Creating a 30 year average with this process given the parameters should squash the time 
dimension down from x (where x is the number of days in the input data) to 1 in the output data. 
"""
def test_nc_data(url):
    output_data = nc_to_dataset(url)
    assert output_data.dimensions['time'].size == 1
```


```python
# Test normal output data
url = get_metalink_content(output.get()[0])
test_nc_data(url[0])
```

## Multiple File Run
**Dry Run -** Checks files to ensure compatible with process


```python
# process dry run for multiple files
dry_output = thunderbird.generate_climos(
    netcdf=[seasonal_opendap, annual_opendap], 
    operation=operation, 
    climo=climo, 
    resolutions=resolutions, 
    dry_run=dry_run
)
```


```python
# Test dry output for multiple files
metalinks = get_metalink_content(dry_output.get()[0])
assert len(metalinks) == 2
    
for link, tr in zip(metalinks, ['seasonal', 'yearly']):
    output_data = txt_to_string(link)
    assert re.search(r'time_resolution: {}'.format(tr), output_data)
```

**Normal Run**


```python
# Process normal output for multiple files

output = thunderbird.generate_climos(
    netcdf=[seasonal_opendap,annual_opendap], 
    operation=operation, 
    climo=climo, 
    resolutions=resolutions, 
    dry_run=False
)
```


```python
# Test multiple files
metalinks = get_metalink_content(output.get()[0])
assert len(metalinks) == 2
for url in metalinks:
    test_nc_data(url)
```
