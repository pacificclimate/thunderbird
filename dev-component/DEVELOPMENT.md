# Development

This `docker-compose` is set up for development purposes. It will up a dev instance of `thunderbird` with production settings. All you are required to do is to add the following lines to `birdhouse-config/env.local` running on `dev03`:

```
export EXTRA_CONF_DIRS="/storage/data/projects/comp_support/daccs/birdhouse-config
    ...
    /path/to/thunderbird/dev-component"

...
export THUNDERBIRD_DEV_IMAGE="pcic/thunderbird:[your-tag]"