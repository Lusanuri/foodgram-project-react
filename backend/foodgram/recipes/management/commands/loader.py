import json

from django.conf import settings
from django.core.management.base import BaseCommand

from recipes.models import Ingredient

ALREADY_LOADED_ERROR_MESSAGE = 'В базе уже есть данные.'


class Command(BaseCommand):
    """Для загрузки данных (иннгредиентов) в базу."""
    help = 'Загрузка из json файла'

    def handle(self, *args, **kwargs):
        if Ingredient.objects.exists():
            print(ALREADY_LOADED_ERROR_MESSAGE)
            return
        try:
            with open(f'{settings.BASE_DIR}/data/ingredients.json', 'rb') as f:
                data = json.load(f)

                for value in data:
                    ingredient = Ingredient()
                    ingredient.name = value['name']
                    ingredient.measurement_unit = value['measurement_unit']
                    ingredient.save()
        except ValueError:
            print('Неопределенное значение.')
        except Exception:
            print('Что-то пошло не так!')
        else:
            print('Загрузка завершена.')
