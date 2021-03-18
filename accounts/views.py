from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponse
from django.views.generic.edit import FormView
from django.urls import reverse_lazy


class SignUpView(FormView):
    template_name = 'accounts/signup.html'
    success_url = reverse_lazy('accounts:login')
    form_class = UserCreationForm

    def form_valid(self, form):
        form.save()
        return redirect(self.get_success_url())



def login(request):
    return HttpResponse("Login page.")

def logout(request):
    return HttpResponse("Logout page.")
