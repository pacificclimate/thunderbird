#!/usr/bin/env bash
find downscale/output/ -name "*.nc" -exec update_metadata -u metadata-conversion/updates-downscaled-climo.yaml {} \;