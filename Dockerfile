# vim:set ft=dockerfile:
FROM python:3.7-slim
MAINTAINER https://github.com/pacificclimate/thunderbird
LABEL Description="thunderbird WPS" Vendor="pcic" Version="0.6.0"

ENV DEBIAN_FRONTEND=noninteractive
ENV PIP_INDEX_URL="https://pypi.pacificclimate.org/simple/"

# Update Debian system
RUN apt-get update && apt-get install -y \
    build-essential \
    cdo \
    git \
    # HDF5 libraries for cdo
    libhdf5-serial-dev \
    netcdf-bin \
    libnetcdf-dev && \
    rm -rf /var/lib/apt/lists/* && \
    # this line combats the issue found here:
    # https://superuser.com/questions/1347723/arch-on-wsl-libqt5core-so-5-not-found-despite-being-installed
    strip --remove-section=.note.ABI-tag /usr/lib/x86_64-linux-gnu/libQt5Core.so.5 && \
    # Removing this package prevents a scan failure. It will be reintroduced
    # once 1.24.2 becomes available through the base image.
    # Issue link: https://github.com/advisories/GHSA-mh33-7rrq-662w
    apt-get remove -y python3-urllib3

COPY . /opt/wps

WORKDIR /opt/wps

# Create python environment
RUN ["python", "-m", "venv", "venv"]

# Install WPS
RUN ["/bin/bash", "-c", "source venv/bin/activate && pip install -e ."]

# Start WPS service on port 5001 on 0.0.0.0
EXPOSE 5001
ENTRYPOINT ["/bin/bash", "-c"]
CMD ["source venv/bin/activate && exec thunderbird start -b 0.0.0.0"]

# docker build -t pacificclimate/thunderbird .
# docker run -p 5001:5001 pacificclimate/thunderbird
# http://localhost:5001/wps?request=GetCapabilities&service=WPS
# http://localhost:5001/wps?request=DescribeProcess&service=WPS&identifier=all&version=1.0.0
