import json

from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    def handle(self, *args, **options):
        self.import_ingredients()
        print("Загрузка завершена.")

    def import_ingredients(self, file="ingredients.json"):
        file_path = f"../data/{file}"
        with open(file_path, "r") as file:
            data = json.load(file)

            for item in data:
                name = item["name"]
                measurement_unit = item["measurement_unit"]

                ingredient = Ingredient(
                    name=name, measurement_unit=measurement_unit
                )
                ingredient.save()
