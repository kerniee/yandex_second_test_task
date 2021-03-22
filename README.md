# Зависимости
- Docker
- Docker Compose  
Внешние python библиотеки явно описаны в файле `requirements.txt`

### Установка зависимостей
https://docs.docker.com/engine/install/  
https://docs.docker.com/compose/install/

# Запуск сервиса
- Склонировать репозиторий
- Перейти в склонированную директорию
- Запустить командой `docker-compose up`

# Запуск тестов
По умолчанию тесты запускаются каждый раз, когда сервис стартует.
Чтобы отключить такое поведение, в файле `.env` поменяйте `RUN_TESTS=True` на `RUN_TESTS=False`  
### Запуск тестов без docker
- Опционально: Создайте виртуальное окружение python
- Установите зависимости командой `pip install requirements.txt`
- Выполните команду `pytest source/app/tests` 
