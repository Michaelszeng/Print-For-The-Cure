import datetime
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

# Create your models here.
class Donor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    ppe = models.IntegerField(default=0)
    requests = models.IntegerField(default=0)
    shields = models.IntegerField(default=0)
    straps = models.IntegerField(default=0)
    openers = models.IntegerField(default=0)
    handles = models.IntegerField(default=0)
    lat = models.FloatField(default = 0.0)
    lng = models.FloatField(default = 0.0)
    address = models.CharField(max_length=255, default='')
    city = models.CharField(max_length=255, default='')
    state = models.CharField(max_length=2, default='')
    country = models.CharField(max_length=100, default='')
    zipCode = models.CharField(max_length=10, default='')
    registrationDate = models.DateTimeField('date registered')

class RequestModel(models.Model):
    status = models.IntegerField(default=0)     #0 = unclaimed, 1 = claimed
    fName = models.CharField(max_length=100)
    lName = models.CharField(max_length=100)
    email = models.CharField(max_length=255)
    phone = models.CharField(max_length=12)
    numPPE = models.IntegerField(default=0)
    typePPE = models.CharField(max_length=255)
    typeHandle = models.CharField(max_length=255)
    address = models.TextField()
    lat = models.FloatField(default = 0.0)
    lng = models.FloatField(default = 0.0)
    organization = models.TextField()
    city = models.CharField(max_length=255)
    state = models.CharField(max_length=2)
    country = models.CharField(max_length=100)
    zipCode = models.CharField(max_length=10)
    delivDate = models.DateField('date for delivery')
    orderDate = models.DateField('date ordered')
    notes = models.TextField()

    def __str__(self):
        return self.email

class Email(models.Model):
    recipient = models.CharField(max_length=255)
    subject = models.CharField(max_length=255)
    sentDate = models.DateField('date sent')

    def __str__(self):
        return self.recipient + ": " + self.subject + "   " + "Sent: " + str(self.sentDate)
