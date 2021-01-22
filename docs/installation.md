# Installation

- [Install from Github](#install-from-github)
- [Start `thunderbird` PyWPS service](#start-thunderbird-pywps-service)
- [Run `thunderbird` as Docker container](#run-thunderbird-as-docker-container)
- [Use Ansible to deploy `thunderbird` on your System](#use-ansible-to-deploy-thunderbird-on-your-system)

## Install from GitHub

Check out code from the thunderbird GitHub repo and start the installation:
```
$ git clone https://github.com/pacificclimate/thunderbird.git
$ cd thunderbird
```

Create Python environment named `venv`:
```
$ python3 -m venv venv
$ source venv/bin/activate
```

Install requirements:
```
(venv)$ pip install -r requirements.txt
```

Install thunderbird app:
```
(venv)$ pip install -e .
# OR
$ make install
```

For development you can use this command:
```
$ pip install -e .[dev]
# OR
$ make develop
```

## Start `thunderbird` PyWPS service
After successful installation you can start the service using the `thunderbird` command-line.

```
(venv)$ thunderbird --help # show help
(venv)$ thunderbird start  # start service with default configuration

# OR

(venv)$ thunderbird start --daemon # start service as daemon
loading configuration
forked process id: 42
```
The deployed WPS service is by default available on:

http://localhost:5000/wps?service=WPS&version=1.0.0&request=GetCapabilities.

NOTE:: Remember the process ID (PID) so you can stop the service with `kill PID`.

You can find which process uses a given port using the following command (here for port `5000`):

```
$ netstat -nlp | grep :5000
```

Check the log files for errors:
```
$ tail -f  pywps.log
```
... or do it the lazy way

You can also use the `Makefile` to start and stop the service:
```
$ make start
$ make status
$ tail -f pywps.log
$ make stop
```

## Run `thunderbird` as Docker container
You can also run `thunderbird` as a Docker container.
```
$ docker-compose build
$ docker-compose up
```

`thunderbird` will be available on port `8099`.

## Use Ansible to deploy `thunderbird` on your System
Use the [Ansible playbook](http://ansible-wps-playbook.readthedocs.io/en/latest/index.html) for PyWPS to deploy `thunderbird` on your system.
