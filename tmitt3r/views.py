from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView
from django.views.generic.detail import DetailView
from django.urls import reverse_lazy
from .models import Tm33t

def add_like_state(queryset, user):
    for tm33t in queryset:
        if tm33t.has_been_liked(user):
            tm33t.state = 'like'
        else:
            tm33t.state = 'unlike'
    return queryset


def index(request):
    return render(request, 'tmitt3r/index.html')


class HomeView(LoginRequiredMixin, ListView):
    template_name = 'tmitt3r/home.html'
    context_object_name = 'latest_tm33t_list'

    def get_queryset(self):
        """
        ログイン中のユーザーの最近の10個のツイートを取得
        """
        queryset = Tm33t.objects.filter(poster=self.request.user).order_by('-post_time')[:10]
        queryset = add_like_state(queryset, self.request.user)
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['name'] = 'You'
        return context


class Tm33tView(LoginRequiredMixin, CreateView):
    model = Tm33t
    fields = ['content']
    template_name = 'tmitt3r/tm33t.html'
    success_url = reverse_lazy('tmitt3r:home')

    def form_valid(self, form):
        form.instance.poster = self.request.user
        return super().form_valid(form)


class Tm33tDetailView(LoginRequiredMixin, DetailView):
    model = Tm33t
    context_object_name = 'tm33t'
    template_name = 'tmitt3r/tm33t_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tm33t = context.get('tm33t')
        if tm33t.has_been_liked(self.request.user):
            tm33t.state = 'unlike'
        else:
            tm33t.state = 'like'
