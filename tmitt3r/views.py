from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView
from django.utils import timezone
from django.urls import reverse_lazy
from .models import Tm33t


def index(request):
    return render(request, 'tmitt3r/index.html')

class HomeView(LoginRequiredMixin, ListView):
    template_name = 'tmitt3r/home.html'
    context_object_name = 'latest_tm33t_list'

    def get_queryset(self):
        """
        ログイン中のユーザーの最近の10個のツイートを取得
        """
        return Tm33t.objects.filter(poster=self.request.user).order_by('-post_time')[:10]


class Tm33tView(LoginRequiredMixin, CreateView):
    model = Tm33t
    fields = ['content']
    template_name = 'tmitt3r/tm33t.html'
    success_url = reverse_lazy('tmitt3r:home')

    def form_valid(self, form):
        form.instance.poster = self.request.user
        form.instance.post_time = timezone.now()
        return super().form_valid(form)
