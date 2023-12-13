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
                    contact.id = int(row[0])  # Assuming 'id' is in the first column
                    contact.price = row[9]
                    contact.name = row[1]
                    contact.phone_number = row[2]
                    contact.phone_other = row[3]
                    contact.url = row[4]
                    contact.city = row[5]
                    contact.state = row[6]
                    contact.home_type = row[8]
                    contact.address = row[7]
                    contact.save()
                    print("Adding contact %s" % contact.address)
                except (ValueError, IndexError) as e:
                    print(f"Error processing row: {row}. {e}")