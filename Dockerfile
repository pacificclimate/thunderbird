# vim:set ft=dockerfile:
FROM python:3.9-slim
MAINTAINER https://github.com/pacificclimate/thunderbird
LABEL Description="thunderbird WPS" Vendor="pcic" Version="1.2.2"

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
    # Combats the issue found here:
    # https://superuser.com/questions/1347723/arch-on-wsl-libqt5core-so-5-not-found-despite-being-installed
    strip --remove-section=.note.ABI-tag /usr/lib/x86_64-linux-gnu/libQt5Core.so.5 && \
    # Removing this package prevents a scan failure. It will be reintroduced
    # once 1.24.2 becomes available through the base image.
    # Issue link: https://github.com/advisories/GHSA-mh33-7rrq-662w
    apt-get remove -y python3-urllib3 python3-pil python3-pandas libmariadb3 && \
    # Removing this metadata helps prevent issues from vulnerability scan
    rm -f /usr/local/lib/python3.9/site-packages/pip-21.0.1.dist-info/METADATA


COPY . /opt/wps

WORKDIR /opt/wps

# Install WPS
RUN pip install . && \
    pip install gunicorn

# Start WPS service on port 5000 on 0.0.0.0
EXPOSE 5000
CMD ["gunicorn", "--bind=0.0.0.0:5000", "thunderbird.wsgi:application"]

# docker build -t pacificclimate/thunderbird .
# docker run -p 5000:5000 pacificclimate/thunderbird
# http://localhost:5000/wps?request=GetCapabilities&service=WPS
# http://localhost:5000/wps?request=DescribeProcess&service=WPS&identifier=all&version=1.0.0
