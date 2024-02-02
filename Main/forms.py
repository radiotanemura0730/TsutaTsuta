from django import forms

from .models import CustomUser


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ["icon", "username", "user_id", "gakubu", "gakka", "introduce"]
