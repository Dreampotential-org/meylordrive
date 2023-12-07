from django.core.management.base import BaseCommand
from drive.models import Contact
import csv

class Command(BaseCommand):
    help = 'Import address extra'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):

        # ['id', 'owner_name', 'owner_phone', 'owner_phone_other', 'url', 'city', 'state', 'address_text', 'home_type', 'price', 'crawled']
        with open("leads.csv", newline='', encoding='utf-8') as csvfile:
            leadsreader = csv.reader(csvfile)
            Contact.objects.filter().delete()
            for row in leadsreader:
                print(row)
                try:
                    contact = Contact()
                    Contact.price=row[9]
                    Contact.name=row[1]
                    Contact.phone_number=row[2]
                    Contact.phone_other=row[3]
                    Contact.url=row[4]
                    Contact.city=row[5]
                    Contact.state=row[6]
                    Contact.home_type=row[8]
                    Contact.address=row[7]
                    contact.save()
                    print("Adding contact %s" % Contact.address)
                except (ValueError, IndexError) as e:
                    print(f"Error processing row: {row}. {e}")
