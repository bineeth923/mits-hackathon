import pyotp
from django.conf import settings
from django.shortcuts import render, redirect

# Create your views here.
from django.views import View

from bloodfinder.models import Request, PhoneNumber, Donor, SMSBuffer, Districts, BloodGroups

opt_key = "TMJHD4GPFOJQNKD3"

'''
Web Portal

Features:

* Registration
* Request Blood
'''


def portal_index(request):
    return render(request, "bloodfinder/web_index.html")

def portal_success(request):
    return render(request, 'bloodfinder/portal_sucess.html')


class PortalRequestBlood(View):
    def get(self, request):
        return render(request, 'bloodfinder/request.html', {
            'districts':Districts.CHOICES,
            'blood_groups': BloodGroups.CHOICES
        })

    def post(self, request):
        request_ = Request()
        if PhoneNumber.objects.filter(phone=request.POST['phone']).exists():
            phone = PhoneNumber.objects.get(phone=request.POST['phone'])
        else:
            phone = PhoneNumber(phone=request.POST['phone'])
            phone.save()
        request_.phone = phone
        request_.blood_group = request.POST['blood_group']
        request_.high_volume = 'high_volume' in request.POST
        request_.district = request.POST['district']
        request_.save()
        return redirect('portal_success')


class PortalRegistrationPhoneVerify(View):
    def get(self, request):
        return render(request, 'bloodfinder/portal_registration.html', {
            'districts':Districts.CHOICES,
            'blood_groups': BloodGroups.CHOICES
        })

    def post(self, request):
        request.session['context'] = {'phone': request.POST['phone'], 'name': request.POST['name'],
                                      'district': request.POST['district'],
                                      'blood_group': request.POST['blood_group']}
        sms = SMSBuffer()
        sms.sender = "BDF-VERIFY"
        sms.to = request.POST['phone']
        sms.message = "Your OTP is " + pyotp.TOTP(opt_key).now()
        sms.save()
        return redirect('portal_donor_registration')


class PortalDonorRegistration(View):
    def get(self, request):
        return render(request, 'bloodfinder/portal_registration_otp.html')

    def post(self, request):
        otp = request.POST['otp']
        if pyotp.TOTP(opt_key).verify(otp, valid_window=300):
            context = request.session['context']
            donor = Donor()
            donor.phone = context['phone']
            donor.name = context['name']
            donor.district = context['district']
            donor.blood_group = context['blood_group']
            donor.save()
            del request.session['context']
        else:
            return render(request, 'bloodfinder/portal_registration_otp.html', {'error': 'Incorrect OTP'})
        redirect('portal_success')


'''
Admin Views

Features:
* Update Donor Settings
* Registration
* Analytics
* Complaints

'''
