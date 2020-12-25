#!/bin/sh

BASEDIR=$(dirname $(readlink -f "${0}"))
echo $BASEDIR

uwsgi \
	--http 127.0.0.1:8000 \
	--plugins python37 \
	--module "escaperoom.wsgi" \
	--process 1 \
	--threads 1 \
	--static-map /static="${BASEDIR}/static"
