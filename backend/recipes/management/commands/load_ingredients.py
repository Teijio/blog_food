import json

from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    def import_ingredients(self, file="ingredients.json"):
        file_path = f"data/{file}"
        try:
            with open(file_path, "r") as file:
                data = json.load(file)

                for item in data:
                    name = item["name"]
                    measurement_unit = item["measurement_unit"]

                    ingredient = Ingredient(
                        name=name, measurement_unit=measurement_unit
                    )
                    ingredient.save()

                self.stdout.write(
                    self.style.SUCCESS("Данные успешно загружены.")
                )
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f"Файл '{file}' не найден."))
        except json.JSONDecodeError:
            self.stdout.write(self.style.ERROR("Формат не соответствует."))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Произошла ошибка: {str(e)}"))

    def handle(self, *args, **options):
        self.import_ingredients()

