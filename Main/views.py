from django.shortcuts import render

# Create your views here.
from django.views.generic import CreateView, TemplateView
from django.urls import reverse_lazy
from .forms import SignUpForm

class SignUpView(CreateView):
    form_class = SignUpForm
    template_name = 'Main/signup.html'
    success_url = reverse_lazy('signup_auth.html')

class SignUpAuthView(TemplateView):
    template_name = 'Main/signup_auth.html'
