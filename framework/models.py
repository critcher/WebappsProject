from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.db import models

class CalendarUser(models.Model):
    user = models.OneToOneField(User)

class Calendar(models.Model):
    owner = models.OneToOneField(CalendarUser, on_delete=models.CASCADE)

class Event(models.Model):
    description = models.CharField(blank=True, max_length=100)
    name = models.CharField(blank=True, max_length=60)
    start_timestamp = models.DateTimeField()
    end_timestamp = models.DateTimeField()
    icon_url = models.CharField(blank=True, max_length=256)
    calendar = models.ForeignKey(Calendar, on_delete=models.CASCADE)

class App(models.Model):
    description = models.CharField(blank=True, max_length=1000)
    name = models.CharField(max_length=60)
    # Can be used to detect that a user's AppSettings are out of
    # date and might need to be prompted again
    version = models.CharField(max_length=60)
    icon_url = models.CharField(blank=True, max_length=256)
    # URL that we send a GET request to in order to find out what
    # settings the user can set. If blank, no special settings
    # are needed
    settings_url = models.CharField(blank=True, max_length=256)
    # URL that we send the request to in order to get the actual
    # data from the app
    data_url = models.CharField(max_length=256)
    # True if the app should be allowed to be added to a calendar
    # multiple times (with different settings, maybe)
    allow_duplicates = models.BooleanField(default=True)
