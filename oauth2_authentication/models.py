# Based on code provided by:
# https://developers.google.com/api-client-library/python/guide/django

from __future__ import unicode_literals

from django.db import models

from django.contrib.auth.models import User
from oauth2client.django_orm import FlowField, CredentialsField


class FlowModel(models.Model):
    id = models.ForeignKey(User, primary_key=True)
    flow = FlowField()


class CredentialsModel(models.Model):
    id = models.ForeignKey(User, primary_key=True)
    credential = CredentialsField()
