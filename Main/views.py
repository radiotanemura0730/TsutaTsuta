from django.shortcuts import render,redirect

# Create your views here.
from django.views.generic import CreateView, TemplateView
from django.urls import reverse_lazy
from .forms import SignUpForm
from .models import CustomUser
from django.shortcuts import get_object_or_404
from django.core.mail import send_mail
import random

class SignUpView(CreateView):
    form_class = SignUpForm
    template_name = 'Main/signup.html'

    def form_valid(self, form):
        super().form_valid(form)
        random_number = random.randint(1000,9999)
        random_number_str = str(random_number)
        to_email = form.cleaned_data['email']
        subject = "題名"
        message = "認証番号の" + random_number_str + "を入力してください"
        from_email = "system@example.com"
        recipient_list = [to_email]
        send_mail(subject, message, from_email, recipient_list, fail_silently=False)
        print("send_email")
        user_record = CustomUser.objects.get(email=to_email)
        self.user_id = int(user_record.id)
        return redirect("signup_auth", user_id=self.object.id)
    
    def get_success_url(self) -> str:
        return reverse_lazy('signup_auth', kwargs={'user_id' : self.object.id})
    
    
class SignUpAuthView(TemplateView):
    template_name = 'Main/signup_auth.html'
    

    # def get(self, **kwargs):
    #     # <id>を取得
    #     id = kwargs.get('id')
        
    #     # ここでid_paramを使って必要な処理を行う
    #     context={"id":id}
    #     return self.render_to_response(context)
