# Thunderbird Demo
This demo shows how `thunderbird` is used on `jupyter` with `birdy`.

## Installation
Ensure you have an instance of `thunderbird` running on `localhost` before moving forward.

Prepare the `jupyter lab` environment:
```
$ cd notebooks/
$ python3 -m venv demo_venv
$ source demo_venv/bin/activate
(demo_venv)$ pip install -r demo_requirements.txt
(demo_venv)$ jupyter labextension install @jupyter-widgets/jupyterlab-manager
```

**Note:**
You may need to update `nodejs` in order to see the progress bars. `nvm` may need to be configured to pull the update:
```
$ nvm install 10
$ nvm use 10
```

## Run
Simply start `jupyter` and run the notebook:
```
(demo_venv)$ jupyter lab
```
