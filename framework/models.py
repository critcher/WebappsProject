from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.db import models

class CalendarUser(models.Model):
    user = models.OneToOneField(User)

class Calendar(models.Model):
    owner = models.OneToOneField(CalendarUser, on_delete=models.CASCADE)

class Event(models.Model):
    description = models.CharField(blank=True, max_length=100)
    start_timestamp = models.DateTimeField()
    end_timestamp = models.DateTimeField()
    icon_url = models.CharField(blank=True, max_length=256)
    calendar = models.ForeignKey(Calendar, on_delete=models.CASCADE)
