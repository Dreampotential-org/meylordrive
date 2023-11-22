from django.core.management.base import BaseCommand
from drive.models import Contact
import csv

class Command(BaseCommand):
    help = 'Import address extra'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        with open("leads.csv", newline='', encoding='utf-8') as csvfile:
            leadsreader = csv.reader(csvfile)
            for row in leadsreader:
                try:
                    contact = Contact()
                    Contact.notes=row[0],
                    Contact.price=row[1],  # Ensure that row[1] is a valid decimal number
                    Contact.name=row[2],
                    Contact.phone=row[3],
                    Contact.phone_other=row[4],
                    Contact.url=row[5],
                    Contact.city=row[6],
                    Contact.state=row[7],
                    Contact.none_field=row[8],  # Assuming none_field is in the 9th column
                    
                    contact.save()
                except (ValueError, IndexError) as e:
                    # Handle the exception (e.g., log the error, skip the record)
                    print(f"Error processing row: {row}. {e}")