# vim:set ft=dockerfile:
FROM continuumio/miniconda3
MAINTAINER https://github.com/pacificclimate/thunderbird
LABEL Description="thunderbird WPS" Vendor="Birdhouse" Version="0.1.0"

# Update Debian system
RUN apt-get update && apt-get install -y \
 build-essential \
&& rm -rf /var/lib/apt/lists/*

# Update conda
RUN conda update -n base conda

# Copy WPS project
COPY . /opt/wps

WORKDIR /opt/wps

# Create conda environment
RUN conda env create -n wps -f environment.yml

# Install WPS
RUN ["/bin/bash", "-c", "source activate wps && python setup.py develop"]

# Start WPS service on port 5001 on 0.0.0.0
EXPOSE 5001
ENTRYPOINT ["/bin/bash", "-c"]
CMD ["source activate wps && exec thunderbird start -b 0.0.0.0 -c /opt/wps/etc/demo.cfg"]

# docker build -t pacificclimate/thunderbird .
# docker run -p 5001:5001 pacificclimate/thunderbird
# http://localhost:5001/wps?request=GetCapabilities&service=WPS
# http://localhost:5001/wps?request=DescribeProcess&service=WPS&identifier=all&version=1.0.0
