
from django.db import models


# Create your models here.
from django.utils import timezone


class BloodGroups:
    Ap = 'A+'
    An = 'A-'
    Bp = 'B+'
    Bn = 'B-'
    ABp = 'AB+'
    ABn = 'AB-'
    Op = 'O+'
    On = 'O-'
    CHOICES = (
        (Ap, Ap),
        (An, An),
        (Bp, Bp),
        (Bn, Bn),
        (Op, Op),
        (On, On),
        (ABp, ABp),
        (ABn, ABn)
    )


class Districts:
    CHOICES = (
        ('AL', 'Alappuzha'),
        ('ER', 'Ernakulam'),
        ('ID', 'Idukki'),
        ('KN', 'Kannur'),
        ('KS', 'Kasaragod'),
        ('KL', 'Kollam'),
        ('KT', 'Kottayam'),
        ('KZ', 'Kozhikode'),
        ('MA', 'Malappuram'),
        ('PL', 'Palakad'),
        ('PT', 'Pathanamthitta'),
        ('TV', 'Thiruvananthapuram'),
        ('TS', 'Thrissur'),
        ('WA', 'Wayanad')
    )


class Donor(models.Model):
    name = models.CharField(max_length=250)
    phone = models.CharField(max_length=10, unique=True)
    blood_group = models.CharField(max_length=4, choices=BloodGroups.CHOICES)
    district = models.CharField(max_length=2, choices=Districts.CHOICES)


class PhoneNumber(models.Model):
    """
    For fraud protection, normalize the phone number.
    """
    phone = models.CharField(max_length=10, unique=True)


class Request(models.Model):
    phone = models.ForeignKey(PhoneNumber, on_delete=models.SET_NULL, null=True)
    blood_group = models.CharField(max_length=4, choices=BloodGroups.CHOICES)
    high_volume = models.BooleanField(default=False)
    district = models.CharField(max_length=2, choices=Districts.CHOICES)

    time = models.DateTimeField(default=timezone.now)
    is_completed = models.BooleanField(default=False)
    is_fraudulent = models.BooleanField(default=False)

class RequestRefusedList(models.Model):
    request = models.

class Donations(models.Model):
    donor = models.ForeignKey(Donor, on_delete=models.SET_NULL, null=True)
    request = models.ForeignKey(Request, on_delete=models.SET_NULL, null=True)


class Complaints(models.Model):
    phone = models.ForeignKey(PhoneNumber, on_delete=models.SET_NULL, null=True)
    donor = models.ForeignKey(Donor, on_delete=models.SET_NULL, null=True)
    complaint_by_donor = models.BooleanField(default=False)
    text = models.TextField()
    investigating = models.BooleanField(default=False)
    resolved = models.BooleanField(default=False)
    rejected = models.BooleanField(null=True)


class SMSBuffer(models.Model):
    """
    Not a core model - specific to prototype to simulate SMS transaction
    """
    from_ = models.CharField(max_length=10)
    to = models.CharField(max_length=10)
    message = models.TextField()
