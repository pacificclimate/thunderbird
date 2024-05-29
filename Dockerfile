FROM python:3.10-slim

LABEL Maintainer=https://github.com/pacificclimate/thunderbird Description="thunderbird WPS" Vendor="pcic" Version="1.3.1"
ENV DEBIAN_FRONTEND=noninteractive
ENV PIP_INDEX_URL="https://pypi.pacificclimate.org/simple/"

RUN apt-get update && \
    apt-get install -y cdo curl libhdf5-serial-dev netcdf-bin libnetcdf-dev && \
    rm -rf /var/lib/apt/lists/*

COPY . /tmp
WORKDIR /tmp

RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH=/root/.local/bin:$PATH
RUN poetry install

EXPOSE 5000
CMD ["poetry", "run", "gunicorn", "-t 60", "--bind=0.0.0.0:5000", "thunderbird.wsgi:application"]
