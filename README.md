# DAF

![Django CI](https://github.com/z0rr0/daf/workflows/Django%20CI/badge.svg)
![Version](https://img.shields.io/github/tag/z0rr0/daf.svg)
![License](https://img.shields.io/github/license/z0rr0/daf.svg)

**Django Audio Feed** is a simple web application that allows to create custom RSS podcast feeds.

## Deploy

1. Prepare SQLite database
```sh
cd daf
cp db.sqlite3 db.sqlite3.bak
python manage.py flush --no-input
python manage.py createsuperuser
```
2. Build docker container
```sh
make docker
```
3. Go to deploy host and prepare required files. Example of [uwsgi.ini](./uwsgi.ini). For `local_settings` required variables: `DATABASES`, `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`. 
```sh
conf/local_settings.py
conf/uwsgi.ini
conf/db.sqlite3
```
4. Run docker container
```sh
docker run -d --name daf -p 8084:8084 \
  --volume $PWD/data/conf:/data/conf \
  --volume $PWD/data/media:/var/daf/media \
  --volume $PWD/data/static:/var/daf/static \
  --restart always z0rr0/daf
```
5. Collect static files
```sh
docker exec -it daf /bin/bash -c "cd /var/daf && python manage.py collectstatic --no-input"
```
6. Check HTTP response:
```sh
curl -X GET http://localhost:8084
```
7. If nginx is used as a web-frontend, 
read [documentation](https://uwsgi.readthedocs.io/en/latest/tutorials/Django_and_nginx.html)

## License

This source code is governed by a MIT license that can be found
in the [LICENSE](https://github.com/z0rr0/daf/blob/main/LICENSE) file.