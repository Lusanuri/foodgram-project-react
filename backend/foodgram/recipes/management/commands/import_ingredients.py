import csv

from django.conf import settings
from django.core.management import BaseCommand

from recipes.models import Ingredient

TABLES = {
    Ingredient: "ingredients.csv"
}


class Command(BaseCommand):
    def handle(self, *args, **options):
        filename = f"{settings.BASE_DIR}/../data/ingredients.csv"
        with open(filename, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f, fieldnames=('name', 'measurement_unit'))
            for data in reader:
                ingredient = Ingredient(
                    name=data["name"],
                    measurement_unit=data["measurement_unit"]
                )
                ingredient.save()
