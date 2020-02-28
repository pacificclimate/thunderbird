FROM python:3.7

MAINTAINER https://github.com/pacificclimate/thunderbird
LABEL Description="thunderbird WPS" Vendor="Birdhouse" Version="0.1.0"

# Update Debian system
RUN apt-get update && apt-get install -y \
    build-essential && \
    rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN pip install --upgrade pip

# Copy WPS project
COPY . /opt/wps
WORKDIR /opt/wps

# Create python environment
RUN python3 -m venv venv

# Install WPS
RUN ["/bin/bash", "-c", "source venv/bin/activate && pip install -i https://pypi.pacificclimate.org/simple/ -r requirements.txt && pip install -e ."]

# Start WPS service on port 5001 on 0.0.0.0
EXPOSE 5001
ENTRYPOINT ["/bin/bash", "-c"]
CMD ["source venv/bin/activate && exec thunderbird start -b 0.0.0.0 -c /opt/wps/etc/demo.cfg"]

# docker build -t pacificclimate/thunderbird .
# docker run -p 5001:5001 pacificclimate/thunderbird
# http://localhost:5001/wps?request=GetCapabilities&service=WPS
# http://localhost:5001/wps?request=DescribeProcess&service=WPS&identifier=all&version=1.0.0
