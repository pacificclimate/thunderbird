# wps_update_metadata

#### wps_update_metadata is a process that runs the [update_metadata](https://github.com/pacificclimate/climate-explorer-data-prep#update_metadata-update-metadata-in-a-netcdf-file) module of PCIC Climate Explorer Data Preparation Tools. Here, the client will try to connect to a remote Thunderbird instance using the url parameter.


```python
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning) 

from birdy import WPSClient
from pkg_resources import resource_filename
import os
from wps_tools.testing import get_target_url
from netCDF4 import Dataset
from tempfile import NamedTemporaryFile
from wps_tools.output_handling import auto_construct_outputs, nc_to_dataset

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
thunderbird.update_metadata?
```


    [0;31mSignature:[0m
    [0mthunderbird[0m[0;34m.[0m[0mupdate_metadata[0m[0;34m([0m[0;34m[0m
    [0;34m[0m    [0mnetcdf[0m[0;34m=[0m[0;32mNone[0m[0;34m,[0m[0;34m[0m
    [0;34m[0m    [0mloglevel[0m[0;34m=[0m[0;34m'INFO'[0m[0;34m,[0m[0;34m[0m
    [0;34m[0m    [0mupdates_file[0m[0;34m=[0m[0;32mNone[0m[0;34m,[0m[0;34m[0m
    [0;34m[0m    [0mupdates_string[0m[0;34m=[0m[0;32mNone[0m[0;34m,[0m[0;34m[0m
    [0;34m[0m[0;34m)[0m[0;34m[0m[0;34m[0m[0m
    [0;31mDocstring:[0m
    Update file containing missing, invalid, or incorrectly named global or variable metadata attributes
    
    Parameters
    ----------
    netcdf : ComplexData:mimetype:`application/x-netcdf`, :mimetype:`application/x-ogc-dods`
        NetCDF file
    updates_file : ComplexData:mimetype:`text/x-yaml`
        The filepath of an updates file that specifies what to do to the metadata it finds in the NetCDF file
    updates_string : string
        The string in yaml format that specifies what to do to the metadata it finds in the NetCDF file
    loglevel : {'CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'NOTSET'}string
        Logging level
    
    Returns
    -------
    output : ComplexData:mimetype:`application/x-netcdf`
        Output Netcdf File
    [0;31mFile:[0m      ~/code/birds/thunderbird/</tmp/thunderbird-venv/lib/python3.8/site-packages/birdy/client/base.py-2>
    [0;31mType:[0m      method



#### We can use the docstring to ensure we provide the appropriate parameters.


```python
# run update_metadata with yaml text and opendap netcdf inputs
updates_string = '''
global:
    - institute_id:
    - institute_ID: PCIC
    - address: University House 1 
    - Institution: <- institution
'''
opendap_netcdf = "https://docker-dev03.pcic.uvic.ca/twitcher/ows/proxy/thredds/dodsC/datasets/storage/data/projects/comp_support/daccs/test-data/gdd_annual_CanESM2_rcp85_r1i1p1_1951-2100.nc"
opendap_output = thunderbird.update_metadata(updates_string = updates_string, netcdf = opendap_netcdf)
```


```python
# run update_metadata with yaml file and local netcdf inputs
updates_file = resource_filename('tests', 'metadata-conversion/simple-conversion.yaml')
local_netcdf = resource_filename('tests', 'data/gdd_annual_CanESM2_rcp85_r1i1p1_1951-2100.nc')
local_output = thunderbird.update_metadata(updates_file = updates_file, netcdf = local_netcdf)
```

Access the output data with **nc_to_dataset()** or **auto_construct_outputs()** from wps_tools.output_handling


```python
# NBVAL_IGNORE_OUTPUT
nc_to_dataset(local_output.get()[0])
auto_construct_outputs(local_output.get())
```




    [<class 'netCDF4._netCDF4.Dataset'>
     root group (NETCDF3_CLASSIC data model, file format NETCDF3):
         Conventions: CF-1.4
         version: 1
         frequency: day
         product: output
         modeling_realm: atmos
         realization: 1
         references: Maurer, E.P., Hidalgo, H.G., Das, T., Dettinger, M.D., and Cayan, D.R., 2010.
     The utility of daily large-scale climate data in the assessment of climate
     change impacts on daily streamflow in California. Hydrology and Earth System
     Sciences, 14: 1125-1138.
         comment: Quantile mapping extrapolation based on delta-method; tol=0.001
         contact: Alex Cannon (acannon@uvic.ca)
         driving_institution: Canadian Centre for Climate Modelling and Analysis
         driving_institute_id: CCCma
         driving_experiment: CanESM2, historical+rcp85, r1i1p1
         driving_model_id: CanESM2
         driving_model_ensemble_member: r1i1p1
         driving_experiment_name: historical, RCP8.5
         target_institution: Canadian Forest Service, Natural Resources Canada
         target_institute_id: CFS-NRCan
         target_dataset: ANUSPLIN interpolated Canada daily 300 arc second climate grids
         target_id: ANUSPLIN300
         target_references: McKenney, D.W., Hutchinson, M.F., Papadopol, P., Lawrence, K., Pedlar, J.,
     Campbell, K., Milewska, E., Hopkinson, R., Price, D., and Owen, T.,
     2011. Customized spatial climate models for North America.
     Bulletin of the American Meteorological Society, 92(12): 1611-1622.
     
     Hopkinson, R.F., McKenney, D.W., Milewska, E.J., Hutchinson, M.F.,
     Papadopol, P., Vincent, L.A., 2011. Impact of aligning climatological day
     on gridding daily maximum-minimum temperature and precipitation over Canada.
     Journal of Applied Meteorology and Climatology 50: 1654-1665.
         target_version: canada_daily_standard_grids
         target_history: obtained: 2 April 2012, 14 June 2012, and 30 January 2013
         target_contact: Pia Papadopol (pia.papadopol@nrcan-rncan.gc.ca)
         title: Bias Correction/Constructed Analogue Quantile Mapping (BCCAQ) downscaling model output for Canada
         creation_date: 2013-10-16T15:54:57Z
         history: Tue Jun 23 10:41:16 2020: ncatted -a _FillValue,gdd,m,f,-32768. gdd_annual_CanESM2_rcp85_r1i1p1_1951-2100.nc
         NCO: 4.7.2
         project_id: CMIP5
         initialization_method: 1
         physics_version: 1
         model_id: CanESM2
         experiment_id: rcp85
         institute_ID: PCIC
         address: University House 1
         Institution: Pacific Climate Impacts Consortium (PCIC), Victoria, BC, www.pacificclimate.org
         dimensions(sizes): lon(313), lat(145), time(150)
         variables(dimensions): float64 lon(lon), float64 lat(lat), float64 time(time), float32 gdd(time, lat, lon)
         groups: ]



#### Once the process has completed we can extract the results and ensure it is what we expected.


```python
input_data = Dataset("https://docker-dev03.pcic.uvic.ca/twitcher/ows/proxy/thredds/dodsC/datasets/storage/data/projects/comp_support/daccs/test-data/gdd_annual_CanESM2_rcp85_r1i1p1_1951-2100.nc")

# Expected output metadata determined from the input yaml file
# global:
#     - institute_id:
#     - institute_ID: PCIC
#     - address: University House 1 
#     - Institution: <- institution
expected = {
    "institute_ID": "PCIC",
    "address": "University House 1",
    "Institution": input_data.institution,
}
```


```python
def test_metadata(output):
    output_data = nc_to_dataset(output.get()[0])
    
   # updated metadata
    metadata = {
        "institute_ID": output_data.institute_ID,
        "address": output_data.address,
        "Institution": output_data.Institution,
    }

    assert metadata == expected
```


```python
test_metadata(opendap_output)
test_metadata(local_output)
```
