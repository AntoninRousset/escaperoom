#!/bin/sh

BASEDIR=$(dirname $(readlink -f "${0}"))
echo $BASEDIR

uwsgi \
	--master \
	--plugins python37 \
	--http 0.0.0.0:8000 \
	--module "escaperoom.wsgi" \
	--static-map /static="${BASEDIR}/static"
