import csv

from django.conf import settings
from django.core.management import BaseCommand
from recipes.models import Ingredient


class Command(BaseCommand):
    def handle(self, *args, **options):
        filename = f"{settings.BASE_DIR}/data/ingredients.csv"
        ingredients_to_create = []
        with open(filename, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f, fieldnames=('name', 'measurement_unit'))
            for data in reader:
                ingredient = Ingredient(
                    name=data["name"],
                    measurement_unit=data["measurement_unit"]
                )
                ingredients_to_create.append(ingredient)

        Ingredient.objects.bulk_create(ingredients_to_create)
