from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, Http404
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from django.db import transaction
from django.contrib.auth.decorators import login_required
from forms import RegisterForm
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from mimetypes import guess_type
from django.core import serializers
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
# s3
from s3 import s3_upload

# Create your views here.


def home(request):
    context = {}
    context['errors'] = []
    context['messages'] = []
    # in template check for user.is_authenticated
    context['user'] = request.user
    return render(request, 'main.html', context)


@transaction.atomic
def register(request):
    context = {}
    context['errors'] = []
    if request.method == 'GET':
        context['form'] = RegisterForm()
        return render(request, 'registration.html', context)
    form = RegisterForm(request.POST)
    context['form'] = form

    if not form.is_valid():
        return render(request, 'registration.html', context)

    registeredUser = User.objects.create_user(username=form.cleaned_data['username'],
                                              password=form.cleaned_data[
                                                  'password1'],
                                              first_name=form.cleaned_data[
                                                  'first_name'],
                                              last_name=form.cleaned_data[
                                                  'last_name'],
                                              email=form.cleaned_data['email'])
    registeredUser.backend = 'django.contrib.auth.backends.ModelBackend'
    registeredUser.is_active = False
    registeredUser.save()

    token = default_token_generator.make_token(registeredUser)
    email_body = """
    Please click the link below to
    verify your email address and complete the registration of your account:
    http://%s%s""" % (request.get_host(), reverse('confirm', args=(registeredUser.username, token)))

    send_mail(subject="Verify your email address",
              message=email_body,
              from_email="LETS_MAKE_AN_EMAIL_FOR_THIS@GMAIL.COM",
              recipient_list=[registeredUser.email])

    context['email'] = form.cleaned_data['email']
    context['errors'].append("Needs confirmation!")
    return render(request, 'main.html', context)


@transaction.atomic
def confirm_registration(request, username, token):
    user = get_object_or_404(User, username=username)

    # Send 404 error if token is invalid
    if not default_token_generator.check_token(user, token):
        raise Http404

    # Otherwise token was valid, activate the user.
    user.is_active = True
    user.save()
    return render(request, 'main.html', {'errors': ["confirmed!"]})
