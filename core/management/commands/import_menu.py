import csv
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from core.models import Vendor, Category, Product


class Command(BaseCommand):
    help = "Import ByteBites menu data"

    def handle(self, *args, **kwargs):
        self.stdout.write("=" * 50)
        self.stdout.write(self.style.SUCCESS("ByteBites Menu Import"))
        self.stdout.write("=" * 50)

        self.import_vendors()
        self.import_categories()
        self.import_products()

        self.stdout.write("=" * 50)
        self.stdout.write(
            self.style.SUCCESS("Import Completed Successfully!")
        )
        self.stdout.write("=" * 50)

    # ---------------------------------------
    # Import Vendors
    # ---------------------------------------

    def import_vendors(self):

        csv_path = Path(settings.BASE_DIR) / "data" / "vendors.csv"

        with open(csv_path, newline="", encoding="utf-8") as file:

            reader = csv.DictReader(file)

            for row in reader:

                Vendor.objects.update_or_create(

                    slug=row["slug"],

                    defaults={
                        "name": row["name"],
                        "description": row["description"],
                        "venue": row["venue"],
                        "minimum_price": row["minimum_price"],
                        "maximum_price": row["maximum_price"],
                        "opening_time": row["opening_time"],
                        "closing_time": row["closing_time"],
                        "estimated_wait": row["estimated_wait"],
                        "rating": row["rating"],
                        "is_active": row["is_active"],
                    },
                )

                self.stdout.write(
                    self.style.SUCCESS(f"Vendor : {row['name']}")
                )

    # ---------------------------------------
    # Import Categories
    # ---------------------------------------

    def import_categories(self):

        csv_path = Path(settings.BASE_DIR) / "data" / "categories.csv"

        with open(csv_path, newline="", encoding="utf-8") as file:

            reader = csv.DictReader(file)

            for row in reader:

                vendor = Vendor.objects.get(name=row["vendor"])

                Category.objects.update_or_create(

                    vendor=vendor,

                    name=row["category"],

                )

                self.stdout.write(
                    self.style.SUCCESS(
                        f"Category : {vendor.name} -> {row['category']}"
                    )
                )

    # ---------------------------------------
    # Import Products
    # ---------------------------------------

    def import_products(self):

        csv_path = Path(settings.BASE_DIR) / "data" / "products.csv"

        with open(csv_path, newline="", encoding="utf-8") as file:

            reader = csv.DictReader(file)

            for row in reader:

                vendor = Vendor.objects.get(name=row["vendor"])

                category = Category.objects.get(
                    vendor=vendor,
                    name=row["category"]
                )

                Product.objects.update_or_create(

                    slug=row["slug"],

                    defaults={

                        "category": category,

                        "name": row["name"],

                        "description": row["description"],

                        "price": row["price"],

                        "is_veg": row["is_veg"] == "True",

                        "preparation_time": row["preparation_time"],

                        "calories": row["calories"],

                        "is_popular": row["is_popular"] == "True",

                        "is_available": row["is_available"] == "True",

                    },
                )

                self.stdout.write(
                    self.style.SUCCESS(
                        f"Product : {row['name']}"
                    )
                )