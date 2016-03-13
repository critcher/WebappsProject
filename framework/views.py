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
from models import CalendarUser
# s3
from s3 import s3_upload

# Create your views here


def home(request):
    context = {}
    context['errors'] = []
    context['messages'] = []
    # in template check for user.is_authenticated
    context['user'] = request.user
    return render(request, 'main.html', context)


def profile(request, userArg):
    context = {}
    context['errors'] = []
    try:
        userMatch = User.objects.get(username__exact=userArg)
    except ObjectDoesNotExist:
        context['errors'].append("could not find object")
        return render(request, 'main.html', context)
    except MultipleObjectsReturned:
        context['errors'].append("multiple objects returned")
        return render(request, 'main.html', context)
    context['author'] = userArg
    context['firstname'] = userMatch.first_name
    context['lastname'] = userMatch.last_name
    try:
        profMatch = CalendarUser.objects.get(user=userMatch)
    except ObjectDoesNotExist:
        context['errors'].append("You dont have a profile yet!")
        return redirect(reverse("editprofile"))
    except MultipleObjectsReturned:
        context['errors'].append("multiple objects returned")
        return render(request, 'main.html', context)

    context['bio'] = profMatch.bio
    context['age'] = profMatch.age
    context['profile'] = profMatch
    return render(request, 'profile.html', context)


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
    if True:
        registeredUser.is_active = True
    else:
        registeredUser.is_active = False

    registeredUser.save()
    newUserProfile = CalendarUser.objects.create(user=registeredUser)
    newUserProfile.save()

    token = default_token_generator.make_token(registeredUser)
    email_body = """
    Please click the link below to
    verify your email address and complete the registration of your account:
    http://%s%s""" % (request.get_host(), reverse('confirm', args=(registeredUser.username, token)))
    if False:
        send_mail(subject="Verify your email address",
                  message=email_body,
                  from_email="bomocho@GMAIL.COM",
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
