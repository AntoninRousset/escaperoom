FROM python:3.9

ENV STATIC_ROOT=/var/www/escaperoom/static/
ENV MEDIA_ROOT=/var/www/escaperoom/media/

EXPOSE 80

RUN curl -fsSL https://deb.nodesource.com/setup_16.x | bash - && \
        apt-get update && \
	apt-get install -qy apt-utils binutils nodejs default-jdk
RUN python3 -m pip install hypercorn hypercorn[uvloop] aioquic hypercorn[h3] \
    --no-cache-dir --no-python-version-warning --disable-pip-version-check
RUN npm install -g npm@latest @openapitools/openapi-generator-cli

WORKDIR /app

COPY ./requirements.txt ./constraints.txt ./
RUN python3 -m pip install -c constraints.txt -r requirements.txt \
    --no-cache-dir --no-color --no-python-version-warning --disable-pip-version-check

COPY ./ ./
RUN python3 manage.py buildfrontends

RUN mkdir -p /var/run/hypercorn /var/www/escaperoom/

COPY ./entrypoint.sh /
ENTRYPOINT ["/entrypoint.sh"]
