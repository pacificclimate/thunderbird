FROM python:3.7-slim

MAINTAINER https://github.com/pacificclimate/thunderbird
LABEL Description="thunderbird WPS" Vendor="Birdhouse" Version="0.6.0"

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
    strip --remove-section=.note.ABI-tag /usr/lib/x86_64-linux-gnu/libQt5Core.so.5

WORKDIR /code

COPY requirements.txt requirements_dev.txt ./

RUN pip install --upgrade pip && \
    pip install -r requirements.txt -r requirements_dev.txt && \
    pip install gunicorn

COPY . .

EXPOSE 5001

CMD ["gunicorn", "--bind=0.0.0.0:5001", "thunderbird.wsgi:application"]

# docker build -t pacificclimate/thunderbird .
# docker run -p 5001:5001 pacificclimate/thunderbird
# http://localhost:5001/wps?request=GetCapabilities&service=WPS
# http://localhost:5001/wps?request=DescribeProcess&service=WPS&identifier=all&version=1.0.0
