import csv

from django.conf import settings
from django.core.management import BaseCommand
from recipes.models import Tag


class Command(BaseCommand):
    def handle(self, *args, **options):
        filename = f"{settings.BASE_DIR}/data/tags.csv"
        tags_to_create = []
        with open(filename, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f, fieldnames=('name', 'color', 'slug'))
            for data in reader:
                tags = Tag(
                    name=data["name"],
                    color=data["color"],
                    slug=data["slug"]
                )
                tags_to_create.append(tags)

        Tag.objects.bulk_create(tags_to_create)
