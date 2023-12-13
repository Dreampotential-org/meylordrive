import pandas

from django.core.management.base import BaseCommand
from dappx.models import UserMonitor, UserProfileInfo, OrganizationMember
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Crawl Agent Links'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        print("Starting here")
        patients = UserMonitor.objects.filter().all()

        for patient in patients:
            # XXX hassan make query in bulk
            profile = UserProfileInfo.objects.filter(
                user=patient.user
            ).first()
            if profile is None:
                
                print(patient.user)

        