from django.core.management import BaseCommand

from bloodfinder.blood_rank import blood_rank
from bloodfinder.models import *
from bloodfinder.views import USER_HOTLINE, DONOR_HOTLINE


class Command(BaseCommand):
    help = "Find new donors"

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE('Sending SMS\n'))
        donations = Donations.objects.filter(is_accepted=None)
        for donation in donations:
            donation.is_accepted = False
            donation.save()
            d = blood_rank(donation.request, top=1)
            don = Donations()
            don.donor = d[0]
            don.request = donation.request
            don.save()
            sms = SMSBuffer()
            sms.sender = DONOR_HOTLINE
            sms.to = don.donor.phone
            sms.message = "There is a request for your blood urgently. Please confirm by replying to this SMS with a YES."
            sms.save()
