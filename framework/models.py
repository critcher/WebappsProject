from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.db import models
from django.core.validators import MaxValueValidator

class CalendarUser(models.Model):
    user = models.OneToOneField(User)