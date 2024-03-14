from django.core.management.base import BaseCommand
from drive.models import Contact
import csv

class Command(BaseCommand):
    help = 'Import address extra'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        # Open the CSV file for reading
        with open("leads.csv", newline='', encoding='utf-8') as csvfile:
            leadsreader = csv.reader(csvfile)

            # Skip the header row
            next(leadsreader, None)

            # Delete existing Contact objects from the database
            Contact.objects.filter().delete()

            # Initialize the id_counter to 1
            id_counter = 1

            # Iterate through each row in the CSV file
            for row in leadsreader:
                print(row)
                try:
                    # Create a new Contact object and populate its fields from the CSV data
                    contact = Contact()
                    contact.price = row[9]
                    contact.name = row[1]
                    contact.phone_number = row[2]
                    contact.phone_other = row[3]
                    contact.url = row[4]
                    contact.city = row[5]
                    contact.state = row[6]
                    contact.home_type = row[8]
                    contact.address = row[7]

                    # Use the id_counter for the id field
                    # contact.id = id_counter

                    # Increment id_counter for the next iteration
                    # id_counter += 1

                    # Save the Contact object to the database
                    contact.save()
                    print(contact.id)
                    # Print a message indicating that the contact was added
                    print("Adding contact %s" % contact.address)
                except (ValueError, IndexError) as e:
                    # Handle errors if there are issues with data conversion or missing columns
                    print(f"Error processing row: {row}. {e}")