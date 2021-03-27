from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import getttext_lazy as _
from tmitt3r.models import Tm33t

class FollowForm(forms.Form):
    pass

class UnfollowForm(forms.Form):
    pass
