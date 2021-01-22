# wps_decompose_flow_vectors

#### wps_decompose_flow_vectors is a process that runs the [decompose_flow_vectors](https://github.com/pacificclimate/climate-explorer-data-prep#decompose_flow_vectors-create-normalized-unit-vector-fields-from-a-vic-routing-file) module of PCIC Climate Explorer Data Preparation Tools. Here, the client will try to connect to a remote Thunderbird instance using the url parameter.


```python
from birdy import WPSClient
import os
from wps_tools.testing import get_target_url
from netCDF4 import Dataset
from tempfile import NamedTemporaryFile
from wps_tools.output_handling import nc_to_dataset, auto_construct_outputs

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
thunderbird.decompose_flow_vectors?
```


    [0;31mSignature:[0m
    [0mthunderbird[0m[0;34m.[0m[0mdecompose_flow_vectors[0m[0;34m([0m[0;34m[0m
    [0;34m[0m    [0mnetcdf[0m[0;34m,[0m[0;34m[0m
    [0;34m[0m    [0mvariable[0m[0;34m,[0m[0;34m[0m
    [0;34m[0m    [0mdest_file[0m[0;34m=[0m[0;32mNone[0m[0;34m,[0m[0;34m[0m
    [0;34m[0m    [0mloglevel[0m[0;34m=[0m[0;34m'INFO'[0m[0;34m,[0m[0;34m[0m
    [0;34m[0m[0;34m)[0m[0;34m[0m[0;34m[0m[0m
    [0;31mDocstring:[0m
    Process an indexed flow direction netCDF into a vectored netCDF suitable for ncWMS display
    
    Parameters
    ----------
    netcdf : ComplexData:mimetype:`application/x-netcdf`, :mimetype:`application/x-ogc-dods`
        NetCDF file
    variable : string
        netCDF variable describing flow direction
    dest_file : string
        destination netCDF file
    loglevel : {'CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'NOTSET'}string
        Logging level
    
    Returns
    -------
    output : ComplexData:mimetype:`application/x-netcdf`
        output netCDF file
    [0;31mFile:[0m      ~/code/birds/thunderbird/</tmp/thunderbird-venv/lib/python3.8/site-packages/birdy/client/base.py-4>
    [0;31mType:[0m      method



#### We can use the docstring to ensure we provide the appropriate parameters.


```python
flow_vectors_file = "https://docker-dev03.pcic.uvic.ca/twitcher/ows/proxy/thredds/dodsC/datasets/storage/data/projects/comp_support/daccs/test-data/sample_flow_parameters.nc"
variable = "Flow_Direction"
dest_file = "output.nc"
output = thunderbird.decompose_flow_vectors(netcdf=flow_vectors_file, variable=variable, dest_file=dest_file)
```

Access the output with nc_to_dataset() or auto_construct_outputs() from wps_tools.output_handling


```python
# NBVAL_IGNORE_OUTPUT
output_data = nc_to_dataset(output.get()[0])
auto_construct_outputs(output.get())
```




    [<class 'netCDF4._netCDF4.Dataset'>
     root group (NETCDF4 data model, file format HDF5):
         GDAL_AREA_OR_POINT: Area
         Conventions: CF-1.5
         GDAL: GDAL 2.1.0, released 2016/04/25
         history: Thu Jan  7 12:06:21 2021 decompose_flow_vectors https://docker-dev03.pcic.uvic.ca/twitcher/ows/proxy/thredds/dodsC/datasets/storage/data/projects/comp_support/daccs/test-data/sample_flow_parameters.nc /tmp/pywps_process_gn_9bjhm/output.nc Flow_Direction
     Wed Sep 27 12:33:37 2017: ncatted -a long_name,Basin_ID,o,c,Basin ID -a long_name,diffusion,o,c,Diffusivity -a units,diffusion,a,c,1/m -a long_name,Flow_Direction,o,c,Flow Direction -a units,Flow_Direction,a,c,1 -a long_name,Flow_Distance,o,c,Flow Distance -a units,Flow_Distance,a,c,m -a long_name,velocity,o,c,Flow Velocity -a units,velocity,a,c,m/s pcic.pnw.rvic.input_20170927.nc
     Wed Sep 27 11:08:09 2017: ncrename -v Band1,diffusion -v Band2,Flow_Distance -v Band3,Basin_ID -v Band4,velocity -v Band5,Flow_Direction rout-param_pnw_0625dd_v7.nc pcic.pnw.rvic.input_20170927.nc
     Wed Sep 27 10:57:40 2017: GDAL CreateCopy( rout-param_pnw_0625dd_v7.nc, ... )
         NCO: "4.6.0"
         DODS.strlen: 0
         dimensions(sizes): lat(187), lon(239)
         variables(dimensions): float64 lat(lat), float64 lon(lon), float64 eastward_Flow_Direction(lat, lon), float64 northward_Flow_Direction(lat, lon)
         groups: ]



#### Once the process has completed we can extract the results and ensure it is what we expected.


```python
input_data = [
    direction
    for subarray in Dataset(flow_vectors_file).variables["Flow_Direction"]
    for direction in subarray
    if direction != "masked"
]
output_eastward =  [
    x_magnitude 
    for subarray in output_data.variables["eastward_Flow_Direction"] 
    for x_magnitude in subarray 
    if x_magnitude != "masked"
]
output_northward = [
    y_magnitude 
    for subarray in output_data.variables["northward_Flow_Direction"] 
    for y_magnitude in subarray 
    if y_magnitude != "masked"
]
```


```python
# Check if input and output data sizes are matching

assert len(input_data) == len(output_eastward)
assert len(output_eastward) == len(output_northward)
```


```python
# Check if input and output outlet positions are matching

outlets = [i for i in range(len(input_data)) if input_data[i] == 9]

# Outlets should have a flow direction of 0
eastward_outlets = [output_eastward[i] for i in range(len(input_data)) if i in outlets]
northward_outlets = [output_northward[i] for i in range(len(input_data)) if i in outlets]
expected_outlets = [0.0 for i in range(len(outlets))]

assert eastward_outlets == expected_outlets
assert northward_outlets == expected_outlets
```
