# thunderbird

***Thunderbird***

*The Thunderbird is a mythical creature that is said to be the dominating force of all natural activity. Located in the Pacific North Western Mountains, the Thunderbird creates booms of thunder by flapping his wings and shoots bolts of lightning from his eyes, when hunters got too close to his home.*

A Web Processing Service for Climate Explorer data preparation.

## Installation

Set up the virtual environment:
```
$ python3 -m venv venv
$ source venv/bin/activate
(venv)$ pip install -i https://pypi.pacificclimate.org/simple/ -r requirements.txt
(venv)$ pip install .
```

**Note:** In order to run `thunderbird` a few packages will also need to be installed.
```
$ sudo apt-get update && apt-get install -y build-essential cdo libhdf5-serial-dev netcdf-bin libnetcdf-dev
```

## Run

Use the built-in `cli`:
```
(venv)$ thunderbird start
(venv)$ thunderbird stop
```
Or use `make`:
```
(venv)$ make start
(venv)$ make stop
```

## Documentation

Learn more about thunderbird in its official [documentation](https://thunderbird.readthedocs.io).

## Contributing

You can find information about contributing in our [Developer Guide](https://thunderbird.readthedocs.io/en/latest/dev_guide.html).

Please use [bumpversion](https://thunderbird.readthedocs.io/en/latest/dev_guide.html#bump-a-new-version) to release a new version.

## License

Free software: GNU General Public License v3

## Credits

This package was created with [Cookiecutter](https://github.com/audreyr/cookiecutter) and the [bird-house/cookiecutter-birdhouse](https://github.com/bird-house/cookiecutter-birdhouse) project template.
