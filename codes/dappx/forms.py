from django import forms
from dappx.models import UserProfileInfo
from django.contrib.auth.models import User


class UserForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput()
    )
    username = forms.CharField(widget=forms.HiddenInput(),
                               required=False)
    email = forms.CharField()

    class Meta():
        model = User
        fields = ('username', 'email', 'password',)


class UserProfileInfoForm(forms.ModelForm):

    class Meta():
        model = UserProfileInfo
        notify_email = forms.EmailField(label='Notify Email')
        fields = ('name', 'notify_email', 'days_sober')
