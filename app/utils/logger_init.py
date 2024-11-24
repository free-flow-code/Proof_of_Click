import logging
import os
from logging.handlers import RotatingFileHandler

# Создаем папку logs, если её ещё нет
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)

# Настройка основного логгера приложения
logger = logging.getLogger("PoC_app")
logger.setLevel(logging.DEBUG)

app_file_handler = RotatingFileHandler(
    os.path.join(log_dir, "PoC_app_logs.log"),
    mode="w",
    maxBytes=5 * 1024 * 1024,  # Максимальный размер файла 5 МБ
    backupCount=3,  # Хранить до 3 резервных файлов
    encoding="utf-8"
)
app_file_handler.setLevel(logging.DEBUG)
app_formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
app_file_handler.setFormatter(app_formatter)
logger.addHandler(app_file_handler)

# Настройка логгера для Celery
celery_poc_logger = logging.getLogger("celery_PoC")
celery_poc_logger.setLevel(logging.INFO)

celery_file_handler = RotatingFileHandler(
    os.path.join(log_dir, "celery_PoC_logs.log"),
    mode="w",
    maxBytes=10 * 1024 * 1024,  # Максимальный размер файла 10 МБ
    backupCount=5,  # Хранить до 5 резервных файлов
    encoding="utf-8"
)
celery_formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
celery_file_handler.setFormatter(celery_formatter)
celery_poc_logger.addHandler(celery_file_handler)
