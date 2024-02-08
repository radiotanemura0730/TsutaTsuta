from django import forms

from .models import CustomUser
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

class SignUpForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ("email", "password1", "password2")
    
    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)
        self.fields['email'].required = True


class SignUpAuthForm(forms.Form):
    auth_number = forms.IntegerField(label='',widget=forms.NumberInput(attrs={'type': 'number'}))

class CustomAuthenticationForm(AuthenticationForm):
    username = forms.EmailField()


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ["icon", "username", "user_id", "gakubu", "gakka", "introduce"]
        labels = {
            "icon": "画像",
            "username": "ユーザーネーム",
            "user_id": "ユーザーID",
            "gakubu": "学部",
            "gakka": "学科",
            "introduce": "自己紹介文",
        }


class UserDeleteForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = "__all__"


class AvailableProductsForm(forms.Form):
    show_available = forms.BooleanField(
        label="販売中のみ表示",
        label_suffix="",
        required=False,
        initial=False,
        widget=forms.CheckboxInput(),
    )


class OnTransactionProductsForm(forms.Form):
    show_available = forms.BooleanField(
        label="出品中のみ表示",
        label_suffix="",
        required=False,
        initial=False,
        widget=forms.CheckboxInput(),
    )
