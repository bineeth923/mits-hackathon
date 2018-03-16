from django.urls import path

from bloodfinder import views

urlpatterns = [
    path('', views.portal_index, name="portal_index"),
    path('register', views.PortalRegistrationPhoneVerify.as_view(), name="portal_registration_phone_verify"),
    path('register/verify', views.PortalDonorRegistration.as_view(), name="portal_donor_registration"),
    path('request', views.PortalRequestBlood.as_view(), name="portal_request_blood"),
    path('success', views.portal_success, name="portal_success"),


]