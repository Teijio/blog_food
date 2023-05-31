import os
import sys
import json
import django

os.environ["DJANGO_SETTINGS_MODULE"] = "config.settings"
sys.path.append("..")
django.setup()

from recipes.models import Ingredient


def load_data_from_json(file_path):
    with open(file_path, "r") as file:
        data = json.load(file)

        for item in data:
            name = item["name"]
            measurement_unit = item["measurement_unit"]

            ingredient = Ingredient(
                name=name, measurement_unit=measurement_unit
            )
            ingredient.save()

    print("Данные успешно загружены.")


file_path = "/mnt/d/Dev/foodgram-project-react/data/ingredients.json"
load_data_from_json(file_path)
