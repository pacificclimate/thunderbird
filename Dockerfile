FROM python:3.11-slim

LABEL Maintainer=https://github.com/pacificclimate/thunderbird Description="thunderbird WPS" Vendor="pcic" Version="1.2.3"
ENV DEBIAN_FRONTEND=noninteractive
ENV PIP_INDEX_URL="https://pypi.pacificclimate.org/simple/"

COPY . /tmp
ADD poetry.lock /tmp
ADD pyproject.toml /tmp
WORKDIR /tmp

RUN apt-get update && \
    apt-get install -y build-essential cdo curl libhdf5-serial-dev netcdf-bin libnetcdf-dev && \
    rm -rf /var/lib/apt/lists/* && \
    # Removing this package prevents a scan failure. It will be reintroduced
    # once 1.24.2 becomes available through the base image.
    # Issue link: https://github.com/advisories/GHSA-mh33-7rrq-662w
    apt-get remove -y python3-urllib3

RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH=/root/.local/bin:$PATH
RUN poetry install && \
    poetry add gunicorn

EXPOSE 5000
CMD ["poetry", "run", "gunicorn", "--bind=0.0.0.0:5000", "thunderbird.wsgi:application"]
