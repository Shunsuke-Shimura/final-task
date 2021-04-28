from django.shortcuts import get_object_or_404, render
from django.http import JsonResponse, HttpResponseBadRequest
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView
from django.views.generic.detail import DetailView
from django.views.generic.base import View
from django.urls import reverse_lazy
from .models import Reply, Tm33t, Retm33t


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
        return queryset


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
        context['tm33t'] = tm33t
        return context


class Tm33tLikeView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        return HttpResponseBadRequest('Tm33tをLikeするにはPOSTメソッドを使用してください。')
    
    def invalid_post(self, request, *args, **kwargs):
        return HttpResponseBadRequest('不適切なPOSTデータです')

    def post(self, request, *args, **kwargs):
        pk = request.POST.get('pk')
        if pk is None:
            return self.invalid_post(request, *args, **kwargs)
        tm33t = get_object_or_404(Tm33t, pk=pk)
        if request.POST.get('like') == 'like':
            tm33t.users_liked.add(request.user)
        else:
            tm33t.users_liked.remove(request.user)
        return JsonResponse({"state": "OK"})


class Tm33tReplyView(LoginRequiredMixin, CreateView):
    model = Reply
    fields = ['content']
    template_name = 'tmitt3r/tm33t_reply.html'
    success_url = reverse_lazy('tmitt3r:home')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # related_tm33t を追加
        related_tm33t_pk = self.kwargs.get('pk')
        related_tm33t = get_object_or_404(Tm33t, pk=related_tm33t_pk)
        context['related_tm33t'] = related_tm33t
        return context

    def form_valid(self, form):
        # posterを設定
        form.instance.poster = self.request.user
        # related_tm33tを設定
        related_tm33t_pk = self.kwargs.get('pk')
        related_tm33t = get_object_or_404(Tm33t, pk=related_tm33t_pk)
        form.instance.related_tm33t = related_tm33t
        return super().form_valid(form)


class Retm33tView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        return HttpResponseBadRequest('Tm33tをRetm33tするにはPOSTメソッドを使用してください。')
    
    def invalid_post(self, request, *args, **kwargs):
        return HttpResponseBadRequest('不適切なPOSTデータです')

    def post(self, request, *args, **kwargs):
        pk = request.POST.get('pk')
        if pk is None:
            return self.invalid_post(request, *args, **kwargs)
        tm33t = get_object_or_404(Tm33t, pk=pk)
        # Retm33tが存在するかどうか確認
        if not Retm33t.objects.filter(poster=request.user, tm33t_retm33ted=tm33t).exists():
            Retm33t.objects.create(poster=request.user, tm33t_retm33ted=tm33t)
        return JsonResponse({"state": "OK"})


class Unretm33tView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        return HttpResponseBadRequest('Tm33tをUnretm33tするにはPOSTメソッドを使用してください。')
    
    def invalid_post(self, request, *args, **kwargs):
        return HttpResponseBadRequest('不適切なPOSTデータです')

    def post(self, request, *args, **kwargs):
        pk = request.POST.get('pk')
        if pk is None:
            return self.invalid_post(request, *args, **kwargs)
        tm33t = get_object_or_404(Tm33t, pk=pk)
        Retm33t.objects.filter(poster=request.user, tm33t_retm33ted=tm33t).delete()
        return JsonResponse({"state": "OK"})
