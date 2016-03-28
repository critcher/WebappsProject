from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.db import models
from django.core.validators import MaxValueValidator
#Google Django Support Library
from oauth2client.django_orm import FlowField, CredentialsField


class FlowModel(models.Model):
    id = models.ForeignKey(User, primary_key=True)
    flow = FlowField()


class CredentialsModel(models.Model):
    id = models.ForeignKey(User, primary_key=True)
    credential = CredentialsField()



class CalendarUser(models.Model):
    user = models.OneToOneField(User, related_name='userPointer')


class Calendar(models.Model):
    owner = models.OneToOneField(CalendarUser, on_delete=models.CASCADE)


class Event(models.Model):
    description = models.CharField(blank=True, max_length=100)
    name = models.CharField(blank=True, max_length=60)
    start_timestamp = models.DateTimeField()
    end_timestamp = models.DateTimeField()
    icon_url = models.CharField(blank=True, max_length=256)
    calendar = models.ForeignKey(Calendar, on_delete=models.CASCADE)
    # A handle to the AppSettings instance that created this event.
    # Blank if this event is a static calendar event.
    source = models.ForeignKey(
        'AppSettings', blank=True, on_delete=models.CASCADE)


class App(models.Model):
    description = models.CharField(blank=True, max_length=1000)
    name = models.CharField(max_length=60)
    # Can be used to detect that a user's AppSettings are out of
    # date and might need to be prompted again
    version = models.CharField(max_length=60)
    icon_url = models.CharField(blank=True, max_length=256)
    # URL that we send a GET request to in order to find out what
    # settings the user can set. Also the URL we send a POST request
    # with the user chosen settings for verification. If blank,
    # no special settings are needed
    settings_url = models.CharField(blank=True, max_length=256)
    # URL that we send the request to in order to get the actual
    # data from the app
    data_url = models.CharField(max_length=256)
    # True if the app should be allowed to be added to a calendar
    # multiple times (with different settings, maybe)
    allow_duplicates = models.BooleanField(default=True)


class Color(models.Model):
    red = models.PositiveIntegerField(
        validators=[MaxValueValidator(255)], default=0)
    green = models.PositiveIntegerField(
        validators=[MaxValueValidator(255)], default=0)
    blue = models.PositiveIntegerField(
        validators=[MaxValueValidator(255)], default=0)


class AppSettings(models.Model):
    user = models.ForeignKey(CalendarUser, on_delete=models.CASCADE)
    settings_json = models.TextField()
    # Can be used to detect that a user's AppSettings are out of
    # date and might need to be prompted again
    version = models.CharField(max_length=60)
    app = models.ForeignKey(App, on_delete=models.CASCADE)
    # Used to let the app know when we last asked for information
    # for this user. Note that the app can still give us data
    # for dates before this timestamp (to update changed events,
    # for example)
    last_updated_timestamp = models.DateTimeField(blank=True)
    color = models.ForeignKey(
        Color, on_delete=models.SET_NULL, null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.color is None:
            c = Color()
            c.save()
            self.color = c
        super(AppSettings, self).save(*args, **kwargs)
