# wps_generate_prsn

#### wps_generate_prsn is a process that runs the [generate_prsn](https://github.com/pacificclimate/climate-explorer-data-prep#generate_prsn-generate-snowfall-file) module of PCIC Climate Explorer Data Preparation Tools. Here, the client will try to connect to a remote Thunderbird instance using the url parameter.


```python
from birdy import WPSClient
import requests
import os
from wps_tools.file_handling import copy_http_content
from wps_tools.testing import get_target_url
from netCDF4 import Dataset
from tempfile import NamedTemporaryFile
from wps_tools.output_handling import auto_construct_outputs, txt_to_string, nc_to_dataset
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
thunderbird.generate_prsn?
```


    [0;31mSignature:[0m
    [0mthunderbird[0m[0;34m.[0m[0mgenerate_prsn[0m[0;34m([0m[0;34m[0m
    [0;34m[0m    [0mprec[0m[0;34m,[0m[0;34m[0m
    [0;34m[0m    [0mtasmin[0m[0;34m=[0m[0;32mNone[0m[0;34m,[0m[0;34m[0m
    [0;34m[0m    [0mtasmax[0m[0;34m=[0m[0;32mNone[0m[0;34m,[0m[0;34m[0m
    [0;34m[0m    [0mdry_run[0m[0;34m=[0m[0;32mNone[0m[0;34m,[0m[0;34m[0m
    [0;34m[0m    [0mchunk_size[0m[0;34m=[0m[0;36m100[0m[0;34m,[0m[0;34m[0m
    [0;34m[0m    [0moutput_file[0m[0;34m=[0m[0;34m'None'[0m[0;34m,[0m[0;34m[0m
    [0;34m[0m    [0mloglevel[0m[0;34m=[0m[0;34m'INFO'[0m[0;34m,[0m[0;34m[0m
    [0;34m[0m[0;34m)[0m[0;34m[0m[0;34m[0m[0m
    [0;31mDocstring:[0m
    Generate precipitation as snow file from precipitation and minimum/maximum temperature data
    
    Parameters
    ----------
    prec : ComplexData:mimetype:`application/x-netcdf`, :mimetype:`application/x-ogc-dods`
        Precipitation file to process
    tasmin : ComplexData:mimetype:`application/x-netcdf`, :mimetype:`application/x-ogc-dods`
        Tasmin file to process
    tasmax : ComplexData:mimetype:`application/x-netcdf`, :mimetype:`application/x-ogc-dods`
        Tasmax file to process
    chunk_size : integer
        Number of time slices to be read/written at a time
    output_file : string
        Optional custom name of output file
    loglevel : {'CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'NOTSET'}string
        Logging level
    dry_run : boolean
        Checks file to ensure compatible with process
    
    Returns
    -------
    output : ComplexData:mimetype:`application/x-netcdf`
        Output Netcdf File
    dry_output : ComplexData:mimetype:`text/plain`
        File information
    [0;31mFile:[0m      ~/code/birds/thunderbird/docs/source/notebooks/</tmp/thunderbird-venv/lib/python3.8/site-packages/birdy/client/base.py-1>
    [0;31mType:[0m      method



#### We can use the docstring to ensure we provide the appropriate parameters.


```python
# Dry-run
pr_file_opendap = "https://docker-dev03.pcic.uvic.ca/twitcher/ows/proxy/thredds/dodsC/datasets/storage/data/projects/comp_support/daccs/test-data/pr_day_BCCAQv2+ANUSPLIN300_NorESM1-M_historical+rcp26_r1i1p1_19500101-19500107.nc"
tasmin_file_opendap = "https://docker-dev03.pcic.uvic.ca/twitcher/ows/proxy/thredds/dodsC/datasets/storage/data/projects/comp_support/daccs/test-data/tasmin_day_BCCAQv2%2BANUSPLIN300_NorESM1-M_historical%2Brcp26_r1i1p1_19500101-19500107.nc"
tasmax_file_opendap = "https://docker-dev03.pcic.uvic.ca/twitcher/ows/proxy/thredds/dodsC/datasets/storage/data/projects/comp_support/daccs/test-data/tasmax_day_BCCAQv2%2BANUSPLIN300_NorESM1-M_historical%2Brcp26_r1i1p1_19500101-19500107.nc"

dry_output = thunderbird.generate_prsn(pr_file_opendap, tasmin_file_opendap, tasmax_file_opendap, chunk_size=50, dry_run=True)
```


```python
req = requests.get(dry_output.get()[0])
dependent_varnames = [line.split(":")[-1].strip(" ['']") for line in req.content.decode('utf-8').split("\n") if "dependent_varnames" in line]
assert dependent_varnames == ['pr', 'tasmin', 'tasmax']
```


```python
# Normal run
output = thunderbird.generate_prsn(pr_file_opendap, tasmin_file_opendap, tasmax_file_opendap, chunk_size=50, dry_run=False, output_file="prsn_test_mixed.nc")
```

Access the output with **auto_construct_outputs()** or **txt_to_string()** and **nc_to_dataset** from wps_tools.output_handling


```python
# NBVAL_IGNORE_OUTPUT
outputs = auto_construct_outputs(dry_output.get() + output.get())
[type(output) for output in outputs]
```




    [str, netCDF4._netCDF4.Dataset]




```python
# NBVAL_IGNORE_OUTPUT
output_data = output.get()[0]
nc_content = nc_to_dataset(output_data)
print(txt_to_string(dry_output.get()[0]))
print(output_data)
```

    Dry Run
    generate_prsn:Dry Run
    INFO:dp.generate_prsn:
    INFO:dp.generate_prsn:File: https://docker-dev03.pcic.uvic.ca/twitcher/ows/proxy/thredds/dodsC/datasets/storage/data/projects/comp_support/daccs/test-data/pr_day_BCCAQv2+ANUSPLIN300_NorESM1-M_historical+rcp26_r1i1p1_19500101-19500107.nc
    INFO:dp.generate_prsn:project: CMIP5
    INFO:dp.generate_prsn:model: NorESM1-M
    INFO:dp.generate_prsn:institute: PCIC
    INFO:dp.generate_prsn:experiment: historical,rcp26
    INFO:dp.generate_prsn:ensemble_member: r1i1p1
    INFO:dp.generate_prsn:dependent_varnames: ['pr']
    INFO:dp.generate_prsn:
    INFO:dp.generate_prsn:File: https://docker-dev03.pcic.uvic.ca/twitcher/ows/proxy/thredds/dodsC/datasets/storage/data/projects/comp_support/daccs/test-data/tasmin_day_BCCAQv2%2BANUSPLIN300_NorESM1-M_historical%2Brcp26_r1i1p1_19500101-19500107.nc
    INFO:dp.generate_prsn:project: CMIP5
    INFO:dp.generate_prsn:model: NorESM1-M
    INFO:dp.generate_prsn:institute: PCIC
    INFO:dp.generate_prsn:experiment: historical,rcp26
    INFO:dp.generate_prsn:ensemble_member: r1i1p1
    INFO:dp.generate_prsn:dependent_varnames: ['tasmin']
    INFO:dp.generate_prsn:
    INFO:dp.generate_prsn:File: https://docker-dev03.pcic.uvic.ca/twitcher/ows/proxy/thredds/dodsC/datasets/storage/data/projects/comp_support/daccs/test-data/tasmax_day_BCCAQv2%2BANUSPLIN300_NorESM1-M_historical%2Brcp26_r1i1p1_19500101-19500107.nc
    INFO:dp.generate_prsn:project: CMIP5
    INFO:dp.generate_prsn:model: NorESM1-M
    INFO:dp.generate_prsn:institute: PCIC
    INFO:dp.generate_prsn:experiment: historical,rcp26
    INFO:dp.generate_prsn:ensemble_member: r1i1p1
    INFO:dp.generate_prsn:dependent_varnames: ['tasmax']
    
    http://localhost:5000/outputs/ad971abc-5466-11eb-9bea-9bfa3f22d465/prsn_test_mixed.nc



```python
assert 'prsn' in nc_content.variables.keys()
```
