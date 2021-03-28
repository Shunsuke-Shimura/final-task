from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class FollowForm(forms.Form):
    username = forms.CharField(max_length=150)

    def clean_username(self):
        username = self.cleaned_data['username']
        if not User.objects.filter(username=username).exists():
            raise ValidationError(_('存在しないusernameです。'))
        return username


class UnfollowForm(forms.Form):
    username = forms.CharField(max_length=150)

    def clean_username(self):
        username = self.cleaned_data['username']
        if not User.objects.filter(username=username).exists():
            raise ValidationError(_('存在しないusernameです。'))
        return username
