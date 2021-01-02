#!/bin/sh

BASEDIR=$(dirname $(readlink -f "${0}"))
ADDR=0.0.0.0:8000


open_when_ready() {
	while wget -q --spider; do
		sleep 1
	done
	xdg-open "http://${ADDR}"
}

open_when_ready &
uwsgi \
	--master \
	--plugins python38 \
	--http "${ADDR}" \
	--module "escaperoom.wsgi" \
	--static-map /static="${BASEDIR}/static" \
	--processes 4 \
	--threads 2 \
