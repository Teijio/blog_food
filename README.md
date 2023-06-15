# Foodgram - продуктовый помощник
[![Python](https://img.shields.io/badge/-Python-464646?style=flat-square&logo=Python)](https://www.python.org/)
[![Nginx](https://img.shields.io/badge/-NGINX-464646?style=flat-square&logo=NGINX)](https://nginx.org/ru/)
[![gunicorn](https://img.shields.io/badge/-gunicorn-464646?style=flat-square&logo=gunicorn)](https://gunicorn.org/)
[![docker](https://img.shields.io/badge/-Docker-464646?style=flat-square&logo=docker)](https://www.docker.com/)
[![GitHub%20Actions](https://img.shields.io/badge/-GitHub%20Actions-464646?style=flat-square&logo=GitHub%20actions)](https://github.com/features/actions)
[![Yandex.Cloud](https://img.shields.io/badge/-Yandex.Cloud-464646?style=flat-square&logo=Yandex.Cloud)](https://cloud.yandex.ru/)
[![DjangoREST](https://img.shields.io/badge/DJANGO-REST-ff1709?style=for-the-badge&logo=django&logoColor=white&color=ff1709&labelColor=gray)](https://www.django-rest-framework.org/)
[![Postgres](https://img.shields.io/badge/postgres-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)

#
Дипломная работа по специальности Python-разработчик курса Яндекс.Практикум. Данная работа является заключительным этапом обучения.
Foodgram - онлайн-сервис, где пользователи смогут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.


## Подготовка сервера

```bash
# Создайте файл .env в директории проекта и укажите в нем:
SECRET_KEY #'< секретный ключ >'
POSTGRES_USER #postgres
POSTGRES_PASSWORD #postgres
POSTGRES_DB  #postgres
DB_NAME #foodgram
DB_HOST #db
DB_PORT #5432

# Добавьте секреты в репозиторий своего проекта.
HOST #011.222.333.444
USER #admin
PASSWORD #password
SSH_KEY #Приватный ключ
DOCKER_USERNAME #Логин от докера
DOCKER_PASSWORD #Пароль от докера

# В файле settings введите свой ip, доменное имя.
ALLOWED_HOSTS #'127.0.0.1, .localhost, 011.222.333.444' - адрес вашего сервера



```

Все действия мы будем выполнять в Docker, docker-compose как на локальной машине так и на сервере ВМ Yandex.Cloud.
Предварительно установим на ВМ в облаке необходимые компоненты для работы:

*1. Подключитесь к своему серверу*

```bash
ssh -i путь_до_закрытого_ключа admin@011.222.333.444
# admin: имя пользователя, под которым будет выполнено подключение к серверу
# 011.222.333.444: IP-адрес сервера
```

*2. Первым делом обновите существующий список пакетов:*
```bash
sudo apt update
```

*3. Теперь обновите установленные в системе пакеты:*
```bash
sudo apt upgrade -y
```

*3. Установите на свой сервер Docker:*
```bash
sudo apt install docker.io
```

*4. Следующая команда загружает версию v2.13.0 и сохраняет исполняемый файл в каталоге /usr/local/bin/docker-compose, в результате чего данное программное обеспечение будет глобально доступно под именем docker-compose:*
```bash
sudo curl -L "https://github.com/docker/compose/releases/download/2.13.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
```

*5. Затем необходимо задать правильные разрешения, чтобы сделать команду docker-compose исполняемой:*
```bash
sudo chmod +x /usr/local/bin/docker-compose
```

*6. Чтобы проверить успешность установки, запустите следующую команду:*
```bash
docker-compose --version
# Вывод будет выглядеть следующим образом:
#docker-compose version 1.26.0, build 8a1c60f6
```

*6. Скопируйте файлы docker-compose.yaml и nginx/default.conf из вашего проекта на сервер в home/<ваш_username>/docker-compose.yaml и home/<ваш_username>/nginx/default.conf соответственно.:*
```bash
#Эти файлы нужно скопировать из директории вашего проекта
scp docker-compose.yml nginx.conf admin@011.222.333.444:/home/admin/
```
## Запуск

Команда git push является триггером workflow проекта. При выполнении команды git push запустится набор блоков команд jobs. Последовательно будут выполнены следующие блоки:

**tests** - тестирование проекта на соответствие PEP8.

**build_and_push_to_docker_hub** - при успешном прохождении тестов собирается образ (image) для docker контейнера и отправляется в DockerHub

**deploy** - после отправки образа на DockerHub начинается деплой проекта на сервере.

После выполнения вышеуказанных процедур необходимо установить соединение с сервером:

```bash
ssh -i путь_до_закрытого_ключа admin@011.222.333.444
```

Выполните по очереди команды:

```bash
sudo docker-compose exec backend python manage.py migrate
sudo docker-compose exec backend python manage.py createsuperuser
sudo docker-compose exec backend python manage.py collectstatic --no-input
sudo docker-compose exec backend python manage.py load_ingredients
```

Теперь проект доступен по адресу http://ваш_ip/.

#

## Документация к API
Чтобы открыть документацию, внутри репозитория есть папка infra.
Перейдите в нее и выполните docker compose up.
Документация будет доступна по localhost/api/docs
#

###
Автор проекта - Артур Шутов
###
Ревьювер - Андрей Белов