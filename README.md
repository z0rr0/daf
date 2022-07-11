# DAF

![Django CI](https://github.com/z0rr0/daf/workflows/Django%20CI/badge.svg)
![Version](https://img.shields.io/github/tag/z0rr0/daf.svg)
![License](https://img.shields.io/github/license/z0rr0/daf.svg)

Django Audio Feed

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
docker build -t daf . 
```
3. Go to deploy host and prepare required files
```sh
conf/local_settings.py
conf/uwsgi.ini
conf/db.sqlite3
```
4. Run docker container
```sh
docker run -d --name daf -p 8084:8084 --volume $PWD/conf:/data/conf --volume $PWD/media:/var/daf/media --restart always daf
```
5. Collect static files
```sh
docker exec -it daf /bin/sh
python manage.py collectstatic --no-input
```
6. Check HTTP response:
```sh
curl -X GET http://localhost:8084
```

## License

This source code is governed by a MIT license that can be found
in the [LICENSE](https://github.com/z0rr0/daf/blob/main/LICENSE) file.