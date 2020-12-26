#!/bin/sh

BASEDIR=$(dirname $(readlink -f "${0}"))
echo $BASEDIR

uwsgi \
	--http 0.0.0.0:8000 \
	--plugins python37,gevent37 \
	--gevent 2 \
	--module "escaperoom.wsgi" \
	--static-map /static="${BASEDIR}/static"
