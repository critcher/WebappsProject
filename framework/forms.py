from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.core.validators import validate_email


class RegisterForm(forms.Form):
    widgetForCSS = forms.TextInput(attrs={'class': 'form-control'})
    passwordWidget = forms.PasswordInput(attrs={'class': 'form-control'})
    username = forms.CharField(
        max_length=20, label="Username", widget=widgetForCSS)
    password1 = forms.CharField(
        max_length=24, label="Password", widget=passwordWidget)
    password2 = forms.CharField(
        max_length=24, label="Re-type Password", widget=passwordWidget)
    first_name = forms.CharField(
        max_length=24, label="First Name", widget=widgetForCSS)
    last_name = forms.CharField(
        max_length=24, label="Last Name", widget=widgetForCSS)
    #email = forms.CharField(max_length=40, widget=widgetForCSS, validators=[validate_email])
    email = forms.CharField(max_length=40, widget=widgetForCSS)

    def clean(self):
        cleanDict = super(RegisterForm, self).clean()
        p1 = cleanDict.get('password1')
        p2 = cleanDict.get('password2')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("Passwords do not match.")
        if User.objects.filter(username__exact=self.cleaned_data.get('username')):
            raise forms.ValidationError("username taken!")
        return cleanDict

class SignInForm(forms.Form):
    widgetForCSS = forms.TextInput(attrs={'class': 'form-control'})
    passwordWidget = forms.PasswordInput(attrs={'class': 'form-control'})
    username = forms.CharField(max_length=20, widget=widgetForCSS)
    password = forms.CharField(max_length=20, widget=passwordWidget)

    user = None

    def is_valid(self):
        valid = super(SignInForm, self).is_valid()
 
        if (not valid):
            return valid
        
        self.user = authenticate(username=self.cleaned_data['username'], password=self.cleaned_data['password'])
        if (not self.user):
            self.add_error(None, "Invalid username/password combination.")
            return False

        if (not self.user.is_active):
            self.add_error(None, "Please activate your account through email first.")
            return False

        return True

class AppSettingsForm(forms.Form):
    placeholder = forms.CharField()