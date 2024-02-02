from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django import forms

User = get_user_model()

class SignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("email", "password1", "password2")
    
    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)
        self.fields['email'].required = True

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['icon', 'username', 'user_id', 'gakubu', 'gakka', 'introduce']

