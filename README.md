# Proof of Click

## Install Python3.9 (Ubuntu)

```shell
sudo apt install build-essential zlib1g-dev \
libncurses5-dev libgdbm-dev libnss3-dev \
libssl-dev libreadline-dev libffi-dev curl software-properties-common
```

`wget https://www.python.org/ftp/python/3.9.0/Python-3.9.0.tar.xz`

`tar -xf Python-3.9.0.tar.xz`

`cd Python-3.9.0`

`./configure`

`sudo make altinstall`

Path to interpreter: `usr/local/bin/python3.9`

## Install nodejs/npm

`sudo apt install nodejs`

`sudo apt install npm`

## Запуск приложения локально

Python 3.9, nodejs 12.22.9, npm 8.5.1 должны быть установлены.
Создайте и активируйте виртуальное окружение и установите зависимости:


```shell
source venv/bin/activate
```

```sh
$ pip install -r requirements.txt
```

Создайте базы данных PostgreSQL 16.3 и Redis. В корне проекта создайте
'.env' файл с переменными окружения:

```
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASS=root
DB_NAME=postgres
DOMAIN=http://mi-site.com
JWT_SECRET_KEY=asdlajsdasASDASD
ALGORITHM=HS256
ORIGINS=["localhost:8000", "127.0.0.1:8000"]
REDIS_HOST=localhost
REDIS_PORT=6379
SMTP_HOST = smtp.mail.com
SMTP_USER = mymail@mail.com
SMTP_PASSWORD=password
SMTP_PORT=465
```

где:

- 'DB_HOST' адрес БД, по умолчанию 'localhost'
- 'DB_PORT' порт БД, по умолчанию '5432'
- 'DB_USER' пользователь БД, по умолчанию 'postgres'
- 'DB_PASS' пароль БД, по умолчанию 'root'
- 'DB_NAME' название БД, по умолчанию 'postgres'
- 'DOMAIN' доменное имя сайта, нужно для реферальной ссылки
- 'JWT_SECRET_KEY' ключ для генерации JWT-токена
- 'ALGORITHM' алгоритм для шифрования JWT-токена, по умолчанию 'HS256'
- 'ORIGINS' список разрешенных адресов для работы с API, по умолчанию '["localhost:8000", "127.0.0.1:8000"]'
- 'REDIS_HOST' адрес redis, по умолчанию 'localhost'
- 'REDIS_PORT' порт redis, по умолчанию '6379'
- SMTP_HOST хост почтового сервера, нет значения по умолчанию
- SMTP_USER адрес почты, для подключения к серверу, нет значения по умолчанию
- SMTP_PASSWORD пароль, для подключения к почтовому серверу, нет значения по умолчанию
- SMTP_PORT порт почтового сервера, нет значения по умолчанию

Примените миграции командой:

```sh
$ alembic upgrade head
```