# Foodgram продуктовый помощник
Сайт Foodgram, «Продуктовый помощник». На этом сервисе пользователи смогут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

http://130.193.50.87/

workflow

Установка
Склонируйте репозиторий
git clone https://github.com/lusanuri/foodgram-project-react.git
Создайте и заполните .env файл
cd foodgram-project-react/backend/foodgram
touch .env
echo DB_ENGINE=django.db.backends.postgresql >> .env
echo DB_NAME=postgres >> .env
echo POSTGRES_PASSWORD=postgres >> .env
echo POSTGRES_USER=postgres >> .env
echo DB_HOST=db >> .env
echo DB_PORT=5432 >> .env
Соберите контейнеры командой
cd ../../infra
docker-compose up -d
Для запуска сервера разработки выполните команды:
docker-compose exec backend python manage.py makemigrateins
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py createsuperuser
docker-compose exec backend python manage.py collectstatic --no-input
docker-compose exec backend python manage.py import_ingredients
docker-compose exec backend python manage.py import_tags
