#!/usr/bin/env sh

set -e

MODULE_NAME=${MODULE_NAME:-project.asgi}
VARIABLE_NAME=${VARIABLE_NAME:-application}
BIND=${BIND:-"/var/run/hypercorn/asgi.sock"}
MODULE=${MODULE:-"$MODULE_NAME:$VARIABLE_NAME"}

if ! python3 manage.py migrate --no-input --check; then
echo 'Initializing'
cat <<EOF | python3 manage.py shell
import os
from django.core.management import call_command

call_command('migrate', '--no-input')
call_command('collectstatic', '-c', '--no-input')

from django.contrib.auth.models import User
print('Creating superuser')
User.objects.create_superuser(
os.environ['USERNAME'], None, os.environ['PASSWORD']
)
EOF
fi

# Start processes
exec hypercorn --umask 777 --bind "${BIND}" "${MODULE}"
