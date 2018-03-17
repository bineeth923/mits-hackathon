import json

import pyotp
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render, redirect

# Create your views here.
from django.views import View
from django.views.decorators.csrf import csrf_exempt, csrf_protect

from bloodfinder.blood_rank import blood_rank
from bloodfinder.models import Request, PhoneNumber, Donor, SMSBuffer, Districts, BloodGroups, Donations

opt_key = "TMJHD4GPFOJQNKD3"

DONOR_HOTLINE = '9898'
USER_HOTLINE = '9999'

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
            'districts': Districts.CHOICES,
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
            'districts': Districts.CHOICES,
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
        print(sms.message)
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
        return redirect('portal_success')


'''
Admin Views

Features:
* Update Donor Settings
* Registration
* Analytics
* Complaints

'''

'''
APIs

* Search
* Update
* Complaint
* Feedback

'''


@csrf_exempt
def api_search(request):
    request_ = Request()
    data = json.loads(request.body)
    print(data)
    if PhoneNumber.objects.filter(phone=data['phone']).exists():
        phone = PhoneNumber.objects.get(phone=data['phone'])
    else:
        phone = PhoneNumber(phone=data['phone'])
        phone.save()
    request_.phone = phone
    request_.blood_group = data['blood_group']
    request_.high_volume = data['high_volume']
    request_.district = data['district']
    request_.save()
    donor_list = blood_rank(request_)
    for donor in donor_list:
        d = Donations()
        d.donor = donor
        d.request = request_
        d.save()
        sms = SMSBuffer()
        sms.sender = DONOR_HOTLINE
        sms.to = donor.phone
        sms.message = "There is a request for your blood urgently. Please confirm by replying to this SMS with a YES."
        sms.save()
        print(sms.message)

    return JsonResponse({'status': 'ok'})


@csrf_exempt
def api_donor_confirm(request):
    number = request.POST['number']
    donation = Donations.objects.get(has_accepted=None, donor__phone=number)
    donation.has_accepted = True
    donation.save()
    return JsonResponse({'status': 'ok'})


@csrf_exempt
def api_user_complete(request):
    number = request.POST['number']
    donations = Donations.objects.filter(has_accepted=True, request__phone__phone=number)
    for donation in donations:
        donation.has_completed = True
        donation.save()
    return JsonResponse({'status': 'ok'})


@csrf_exempt
def get_sms(request):
    num = request.GET['number']
    sms_list = SMSBuffer.objects.filter(to=num, is_sent=False)
    for sms in sms_list:
        print(sms)
        sms.is_sent = True
        sms.save()
    return JsonResponse({'message_list': [i.serialize for i in sms_list]})
