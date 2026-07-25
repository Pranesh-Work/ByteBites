import csv
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from core.models import Vendor, Category


class Command(BaseCommand):
    help = "Import vendors from CSV"

    def handle(self, *args, **kwargs):
        csv_path = Path(settings.BASE_DIR) / "data" / "vendors.csv"

        if not csv_path.exists():
            self.stdout.write(
                self.style.ERROR(f"File not found: {csv_path}")
            )
            return

        with open(csv_path, newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)

            for row in reader:
                vendor, created = Vendor.objects.update_or_create(
                    slug=row["slug"],
                    defaults={
                        "name": row["name"],
                        "description": row["description"],
                        "venue": row["venue"],
                        "minimum_price": row["min_price"],
                        "maximum_price": row["max_price"],
                    },
                )

                if created:
                    self.stdout.write(
                        self.style.SUCCESS(f"Created: {vendor.name}")
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(f"Updated: {vendor.name}")
                    )


        self.stdout.write(self.style.SUCCESS("Menu Import completed successfully."))


