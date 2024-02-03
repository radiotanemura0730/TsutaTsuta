from django import forms

from .models import CustomUser


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
