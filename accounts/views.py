from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import FormView
from django.views.generic.detail import DetailView
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from rest_framework import generics
from accounts.serializers import FollowsSerializer
from accounts.permissions import IsActor
from accounts.models import Follows
from accounts.forms import FollowForm, UnfollowForm


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


class UserDetailView(LoginRequiredMixin, DetailView):
    template_name = 'accounts/profile.html'
    context_object_name = 'profiled_user'
    model = User
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['follow_num'] = Follows.objects.filter(actor=self.object).count()
        context['follower_num'] = Follows.objects.filter(followed_user=self.object).count()
        context['latest_tm33t_list'] = self.object.tm33ts.order_by('-post_time')[:10]
        if self.object != self.request.user:
            if Follows.objects.filter(actor=self.request.user, followed_user=self.object).exists():
                context['following_state'] = 'following'
            else:
                context['following_state'] = 'unfollowing'
        return context


class FollowView(LoginRequiredMixin, FormView):
    template_name = 'accounts/follow.html'
    form_class = FollowForm

    def form_valid(self, form):
        username = form.cleaned_data['username']
        self.target_user = User.objects.get(username=username)
        if self.request.user == self.target_user:
            form.add_error('username', ValidationError(_('自分自身はフォローできません')))
            return self.form_invalid(form)
        elif Follows.objects.filter(actor=self.request.user, followed_user=self.target_user).exists():
            form.add_error('username', ValidationError(_('すでにフォローしています')))
            return self.form_invalid(form)
        else:
            Follows.objects.create(actor=self.request.user, followed_user=self.target_user)
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('accounts:profile', kwargs={'pk': self.target_user.pk})


class UnfollowView(LoginRequiredMixin, FormView):
    template_name = 'accounts/unfollow.html'
    form_class = UnfollowForm

    def form_valid(self, form):
        username = form.cleaned_data['username']
        self.target_user = User.objects.get(username=username)
        if self.request.user == self.target_user:
            form.add_error('username', ValidationError(_('自分自身はアンフォローできません')))
            return self.form_invalid(form)
        else:
            get_object_or_404(Follows, actor=self.request.user, followed_user=self.target_user).delete()
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('accounts:profile', kwargs={'pk': self.target_user.pk})

class FollowsDetail(generics.CreateAPIView, generics.DestroyAPIView):
    serializer_class = FollowsSerializer
    queryset = Follows.objects.all()
    permission_classes = [IsActor]

    def get_object(self):
        followed_user = get_object_or_404(User, pk=self.request.data.get('followed_user'))
        obj = get_object_or_404(self.get_queryset(), actor=self.request.user, followed_user=followed_user)
        self.check_object_permissions(self.request, obj)
        return obj

    def perform_create(self, serializer):
        serializer.save(actor=self.request.user)
