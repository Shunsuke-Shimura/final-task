from django.shortcuts import redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login
from django.views.generic.edit import FormView
from django.urls import reverse_lazy


class SignUpView(FormView):
    template_name = 'accounts/signup.html'
    success_url = reverse_lazy('tmitt3r:home')
    form_class = UserCreationForm

    def form_valid(self, form):
        form.save()
        username = form.cleaned_data['username']
        row_password = form.cleaned_data['password1']
        user = authenticate(username=username, password=row_password)
        login(self.request, user)
        return redirect(self.get_success_url())
