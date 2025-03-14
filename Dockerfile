FROM alpine:3.21
LABEL org.opencontainers.image.authors="me@axv.email" \
        org.opencontainers.image.url="https://hub.docker.com/r/z0rr0/daf" \
        org.opencontainers.image.documentation="https://github.com/z0rr0/daf" \
        org.opencontainers.image.source="https://github.com/z0rr0/daf" \
        org.opencontainers.image.licenses="MIT license" \
        org.opencontainers.image.title="DAF" \
        org.opencontainers.image.description="Django Audio Feed"

# https://docs.djangoproject.com/en/5.0/howto/deployment/wsgi/uwsgi/
# https://uwsgi.readthedocs.io/en/latest/tutorials/Django_and_nginx.html

RUN apk update && apk upgrade
RUN apk add tzdata ca-certificates python3 uwsgi-python3 py3-pip sqlite

# base app dir
ADD daf /var/daf
# clean local files
RUN rm -rf /var/daf/media /var/daf/static /var/daf/daf/local_settings.py /var/daf/db.sqlite3*

ADD requirements.txt /tmp/requirements.txt
RUN pip3 install --break-system-packages -r /tmp/requirements.txt

VOLUME ["/data/conf", "/var/daf/media", "/var/daf/static"]
RUN ln -s /data/conf/local_settings.py /var/daf/daf/local_settings.py
# set properly db path in local_settings.py
# 'NAME': '/var/conf/db.sqlite3',

EXPOSE 8084
WORKDIR /var/daf
ENTRYPOINT ["/usr/sbin/uwsgi"]
CMD ["--ini", "/data/conf/uwsgi.ini"]
