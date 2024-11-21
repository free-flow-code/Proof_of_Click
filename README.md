# Proof of Click

- [Описание](#description)
- [Технологический стек](#stack)
- [Локальный запуск (dev)](#start_local)
  - [Install Python3.9 (Ubuntu)](#install_python)
  - [Install nodejs/npm](#install_npm)
  - [Настройка Redis](#setting_redis)
  - [Запуск Redis Cluster на Windows](#start_redis_win)
  - [Настройка окружения](#setting_env)
  - [Запуск приложения](#start_app)

## Описание <a name="description"></a>
...
## Технологический стек <a name="stack"></a>
...
## Локальный запуск (dev) <a name="start_local"></a>

### Install Python3.9 (Ubuntu) <a name="install_python"></a>

```shell
sudo apt install build-essential zlib1g-dev \
libncurses5-dev libgdbm-dev libnss3-dev \
libssl-dev libreadline-dev libffi-dev curl software-properties-common
```

```shell
wget https://www.python.org/ftp/python/3.9.0/Python-3.9.0.tar.xz
```

```shell
tar -xf Python-3.9.0.tar.xz
```

```shell
cd Python-3.9.0
```

```shell
./configure
```

```shell
sudo make altinstall
```

Path to interpreter: `usr/local/bin/python3.9`

### Install nodejs/npm <a name="install_npm"></a>

```shell
sudo apt install nodejs==12.22.9
```

```shell
sudo apt install npm==8.5.1
```

### Настройка Redis <a name="setting_redis"></a>

Включите аутентификацию на серверах Redis, чтобы требовать аутентификацию перед выполнением любых операций.
Используйте сильные пароли или механизмы аутентификации, предоставляемые Redis.

Включение аутентификации в Redis:

```
#В файле redis.conf установите пароль
requirepass your_password
```
Настройка сетевого доступа: Ограничьте доступ к серверам Redis только для доверенных IP-адресов или подсетей.
Это можно сделать через настройки брандмауэра или конфигурации самого кэш-сервера.

Настройка сетевого доступа в Redis:

```
#В файле redis.conf установите разрешенные IP-адреса
bind 127.0.0.1
```

### Запуск Redis Cluster на Windows <a name="start_redis_win"></a>

Т.к. рекомендуемое минимальное количество нод для кластера равняется 3,
то необходимо создать 3 ноды и объединить их в кластер. В директорию в redis
в вашей системе переместите файлы `redis1.conf`, `redis2.conf`, `redis3.conf`,
`start_redis_cluster.ps1` из директории проекта `redis_helpers`.
Откройте файл `start_redis_cluster.ps1` в текстовом редакторе и подставьте
свои значения путей в переменные `redisServerPath`, `redisCliPath`.
Затем запустите Power Shell, перейдите в директорию с redis
в вашей системе и запустите создание нод и кластера командой:

```shell
.\start_redis_cluster.ps1
```
Ноды будут запущены на адресах `127.0.0.1:7000`, `127.0.0.1:7001`, `127.0.0.1:7002`.

### Настройка окружения <a name="setting_env"></a>

Создайте и активируйте виртуальное окружение и установите зависимости:
```shell
source venv/bin/activate
```
```shell
$ pip install -r requirements.txt
```
Создайте базу данных PostgreSQL 16.3 и запустите кластер Redis 7.4.1. В корне проекта создайте
`.env` файл с переменными окружения:

```
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASS=root
DB_NAME=postgres

FRONTEND_DOMAIN=http://127.0.0.1:3000
BACKEND_DOMAIN=http://127.0.0.1:8000
SEND_CLICKS_PERIOD=3

ENCRYPTION_KEY=s3XUjyntOk0o=
JWT_SECRET_KEY=asdlajsdasASDASD=
ALGORITHM=HS256
ORIGINS=["http://127.0.0.1:8000", "http://127.0.0.1:3000"]
SET_COOKIE_SECURE=False

REDIS_CLUSTER_HOST=localhost
REDIS_CLUSTER_PORT=7000

SMTP_HOST=smtp.mail.com
SMTP_USER=mymail@mail.com
SMTP_PASSWORD=password
SMTP_PORT=465

MAX_BLOCKS=99999999999999999
REDIS_NODE_TAG_1={group1}
REDIS_NODE_TAG_2={group2}
REDIS_NODE_TAG_3={group3}
START_INIT_FUNCS=True
```
где:

- `DB_HOST` адрес БД, по умолчанию 'localhost'
- `DB_PORT` порт БД, по умолчанию '5432'
- `DB_USER` пользователь БД, по умолчанию 'postgres'
- `DB_PASS` пароль БД, по умолчанию 'root'
- `DB_NAME` название БД, по умолчанию 'postgres'


- `FRONTEND_DOMAIN` по умолчанию http://127.0.0.1:3000
- `BACKEND_DOMAIN` по умолчанию http://127.0.0.1:8000
- `SEND_CLICKS_PERIOD` время отправки кликов с фронтенда на бэкенд (в секундах), по умолчанию 3 секунды


- `ENCRYPTION_KEY` ключ для шифрования паролей пользователей, нет значения по умолчанию
- `JWT_SECRET_KEY` ключ для генерации JWT-токена, нет значения по умолчанию
- `ALGORITHM` алгоритм для шифрования JWT-токена, по умолчанию 'HS256'
- `JWT_TOKEN_DELAY_MINUTES` время жизни JWT-токена в минутах, по умолчанию 30
- `ORIGINS` список разрешенных адресов для работы с API, по умолчанию '["http://127.0.0.1:8000", "http://127.0.0.1:3000"]'
- `SET_COOKIE_SECURE` по умолчанию False, установите True, если используете HTTPS


- `REDIS_CLUSTER_HOST` адрес redis кластера, по умолчанию 'localhost'
- `REDIS_CLUSTER_PORT` порт redis кластера, по умолчанию '7000'


- `SMTP_HOST` хост почтового сервера, нет значения по умолчанию
- `SMTP_USER` адрес почты, для подключения к серверу, нет значения по умолчанию
- `SMTP_PASSWORD` пароль, для подключения к почтовому серверу, нет значения по умолчанию
- `SMTP_PORT` порт почтового сервера, нет значения по умолчанию


- `MAX_BLOCKS` максимально возможное количество блоков, доступное для добычи, в проекте. Т.к.
максимум можно добыть 99 999 999 999,999 блоков, то это число равно 100 000 000 000 000
- `REDIS_NODE_TAG_1` тег для ключей в редис, позволяет группировать данные по нодам, по умолчанию '{group1}'
- `REDIS_NODE_TAG_2` тег для ключей в редис, позволяет группировать данные по нодам, по умолчанию '{group2}'
- `REDIS_NODE_TAG_3` тег для ключей в редис, позволяет группировать данные по нодам, по умолчанию '{group3}'
- `START_INIT_FUNCS` запускать или нет функции инициализации при старте приложения, по умолчанию - да (True).
Функции инициализации это - добавить бусты в redis, установить количество игровых предметов в redis,
добавить балансы всех пользователей в redis, добавить данные всех пользователей с автокликером в redis
(для обновления баланса в фоне).

### Запуск приложения <a name="start_app"></a>

Примените миграции командой:
```sh
$ alembic upgrade head
```

Запустите FastAPI:
```shell
uvicorn app.main:app --reload
```

Запустите Celery:
```shell
celery -A app.tasks.celery:celery worker --loglevel=INFO
# для windows дополнительно прописать --pool=solo
```

Запустите фронтенд:
```shell
cd frontend
npm start
```