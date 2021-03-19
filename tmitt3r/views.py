from django.http.response import HttpResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView


def index(request):
    return render(request, 'tmitt3r/index.html')

class HomeView(LoginRequiredMixin, TemplateView):
    template_name = 'tmitt3r/home.html'
