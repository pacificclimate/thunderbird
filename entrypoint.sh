#!/bin/sh

chown -R 1000:1000 /data
exec runuser -u 1000 "$@"