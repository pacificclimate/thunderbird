FROM python:3.8-slim

LABEL Maintainer=https://github.com/pacificclimate/thunderbird Description="thunderbird WPS" Vendor="pcic" Version="1.2.1"
ENV DEBIAN_FRONTEND=noninteractive
ENV PIP_INDEX_URL="https://pypi.pacificclimate.org/simple/"

COPY . /tmp
WORKDIR /tmp

RUN apt-get update && \
    apt-get install -y build-essential cdo libhdf5-serial-dev netcdf-bin libnetcdf-dev && \
    rm -rf /var/lib/apt/lists/* && \
    # this line combats the issue found here:
    # https://superuser.com/questions/1347723/arch-on-wsl-libqt5core-so-5-not-found-despite-being-installed
    strip --remove-section=.note.ABI-tag /usr/lib/x86_64-linux-gnu/libQt5Core.so.5 && \
    # Removing this package prevents a scan failure. It will be reintroduced
    # once 1.24.2 becomes available through the base image.
    # Issue link: https://github.com/advisories/GHSA-mh33-7rrq-662w
    apt-get remove -y python3-urllib3 && \
    pip install . && \
    pip install gunicorn

EXPOSE 5000
CMD ["gunicorn", "--bind=0.0.0.0:5000", "thunderbird.wsgi:application"]