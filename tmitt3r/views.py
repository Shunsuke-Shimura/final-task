from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.views.generic.edit import CreateView
from django.utils import timezone
from django.urls import reverse_lazy
from .models import Tm33t


def index(request):
    return render(request, 'tmitt3r/index.html')

class HomeView(LoginRequiredMixin, TemplateView):
    template_name = 'tmitt3r/home.html'

class Tm33tView(LoginRequiredMixin, CreateView):
    model = Tm33t
    fields = ['content']
    template_name = 'tmitt3r/tm33t.html'
    success_url = reverse_lazy('tmitt3r:home')

    def form_valid(self, form):
        form.instance.poster = self.request.user
        form.instance.post_time = timezone.now()
        return super().form_valid(form)
