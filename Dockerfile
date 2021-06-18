FROM python:3.8-slim

LABEL Maintainer=https://github.com/pacificclimate/thunderbird Description="thunderbird WPS" Vendor="pcic" Version="1.2.3"
ENV DEBIAN_FRONTEND=noninteractive
ENV PIP_INDEX_URL="https://pypi.pacificclimate.org/simple/"

COPY . /tmp
WORKDIR /tmp

RUN apt-get update && \
    apt-get install -y build-essential cdo libhdf5-serial-dev netcdf-bin libnetcdf-dev && \
    rm -rf /var/lib/apt/lists/* && \
    pip install -U pip && \
    pip install . && \
    pip install gunicorn

EXPOSE 5000
CMD gunicorn --bind=0.0.0.0:5000 thunderbird.wsgi:application