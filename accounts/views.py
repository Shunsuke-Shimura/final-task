from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import FormView
from django.views.generic.detail import DetailView
from .models import Follows
from .forms import FollowForm, UnfollowForm


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


class FollowView(FormView):
    template_name = 'follow.html'
    form_class = FollowForm


class UnfollowView(FormView):
    template_name = 'unfollow.html'
    form_class = UnfollowForm
