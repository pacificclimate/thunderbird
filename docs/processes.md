# Processes
- [Decompose Flow Vectors](#decompose-flow-vectors)
- [Generate Climos](#generate_climos)
- [Generate Precipitation as Snow](#generate-precipitation-as-snow)
- [Split Merged Climos](#split-merged-climos)
- [Update Metadata](#update-metadata)

## Decompose Flow Vectors
Process an indexed flow direction netCDF into a vectored netCDF suitable for ncWMS display.

[Notebook Demo](formatted_demos/wps_decompose_flow_vectors_demo.html)

## Generate Climos
Generate files containing climatological means from input files of daily, monthly, or yearly data that adhere to the PCIC metadata standard (and consequently to CMIP5 and CF standards).

[Notebook Demo](formatted_demos/wps_generate_climos_demo.html)

## Generate Precipitation as Snow
Generate precipitation as snow file from precipitation and minimum/maximum temperature data.

[Notebook Demo](formatted_demos/wps_generate_prsn_demo.html)

## Split Merged Climos
Split climo means files into one file per time interval.

[Notebook Demo](formatted_demos/wps_split_merged_climos_demo.html)

## Update Metadata
Update file containing missing, invalid, or incorrectly named global or variable metadata attributes.

[Notebook Demo](formatted_demos/wps_update_metadata_demo.html)
