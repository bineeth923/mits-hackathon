from django.core.management import BaseCommand

from bloodfinder.models import *
from bloodfinder.views import USER_HOTLINE


class Command(BaseCommand):
    help = "Send confirmation SMS to users"

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE('Sending SMS\n'))
        donations = Donations.objects.filter(is_accepted=True,is_completed=False)
        for donation in donations:
            sms = SMSBuffer()
            sms.sender = USER_HOTLINE
            sms.to = donation.request.phone.phone
            sms.message = "Hi, this SMS is to confirm whether your blood request has been completed. Please send YES " \
                          "if completed."
            sms.save()
            self.stdout.write(sms.to)
            self.stdout.write(sms.message)
            self.stdout.write("============")
