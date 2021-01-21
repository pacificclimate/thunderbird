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
make install
```

For development you can use this command:
```
$ pip install -e .[dev]
# OR
$ make develop
```
