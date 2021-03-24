from django.test import TestCase, override_settings
from django.contrib.auth.models import User
from django.db.utils import IntegrityError
from django.urls import reverse
from django.utils import timezone
from .models import Tm33t, Follows
import time

no_csrf_middleware = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


class Tm33tModelTests(TestCase):
    def test_str_conversion(self):
        user = User.objects.create_user(username='Tm33tModelTest')
        text = """Very very very very very very very very very very very very very long text."""
        tm33t = Tm33t.objects.create(poster=user, content=text)
        self.assertEqual(str(tm33t), text[:20])


class FollowsModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='FollowsModelTest')
        self.u1 = User.objects.create_user(username='FollowsModelTest1')
        self.u2 = User.objects.create_user(username='FollowsModelTest2')
    def test_follower_folloed_unique(self):
        """
        actorとfollowed_userに設定されたユーザーは
        データベースでユニークであり、IntegrityErrorを発生するが、
        どちらかが異なれば処理は成功する。
        """
        Follows.objects.create(actor=self.user, followed_user=self.u1)
        Follows.objects.create(actor=self.user, followed_user=self.u2)
        self.assertTrue(Follows.objects.filter(actor=self.user, followed_user=self.u2).exists())
        with self.assertRaises(IntegrityError):
            Follows.objects.create(actor=self.user, followed_user=self.u1)


class HomeViewTests(TestCase):
    def setUp(self):
        username = 'HomeViewTestClient'
        password = 'SamplePassword'
        self.user = User.objects.create_user(username=username, 
                                             password=password)
        self.client.login(username=username, password=password)
        self.text_list = []
        for i in range(20):
            text = 'This is HomeViewTest Tm33t text No.{}.'.format(i)
            Tm33t.objects.create(poster=self.user, content=text)
            self.text_list.append(text)
            time.sleep(0.1)
        self.text_list.reverse()
    
    def test_home_view_context(self):
        """
        HomeViewによって、contextとしてログインユーザーの
        直近の10個のTm33tがlatest_tm33t_listとして
        受け渡される。
        """
        res = self.client.get(reverse('tmitt3r:home'))
        queryset = res.context['latest_tm33t_list']
        for i in range(10):
            self.assertEqual(queryset[i].content, self.text_list[i])    


@override_settings(MIDDLEWARE=no_csrf_middleware)
class Tm33tViewTests(TestCase):
    def setUp(self):
        self.username = 'Tm33tViewTest'
        self.password = 'SamplePassword'
        self.user = User.objects.create_user(username=self.username,
                                             password=self.password)
        self.client.login(username=self.username, password=self.password)
    
    def test_tm33t(self):
        """
        ツイートが成功するとデータベースに登録され、
        posterは投稿者に、post_timeは投稿時の時間になる。
        """
        url = reverse('tmitt3r:tm33t')
        text = 'This is sample tm33t for Tm33tViewTest.'
        data = {'content': text}
        time = timezone.now()
        self.client.post(url, data=data)
        tm33t = Tm33t.objects.filter(
                            poster__username=self.username
                        ).get(
                            post_time__gte=time
                        )
        self.assertEqual(tm33t.content, text)

@override_settings(MIDDLEWARE=no_csrf_middleware)
class UserDetailViewTests(TestCase):
    def setUp(self):
        self.username = 'UserDetailViewTest'
        self.password = 'SamplePassword'
        self.user = User.objects.create_user(username=self.username, password=self.password)
        self.tar_user = User.objects.create_user(username='UDVTest')
        self.client.login(username=self.username, password=self.password)
        self.url = reverse('tmitt3r:profile', args=[self.tar_user.pk])

    def test_follow_post(self):
        """
        POSTメソッドにおいてfollows=followなら、
        ログインユーザーはそのプロフィールのユーザーを
        フォローする。
        """
        self.client.post(self.url, data=dict(follows='follow'))
        self.assertTrue(Follows.objects.get(actor=self.user, followed_user=self.tar_user).exists())

    def test_unfollow_post(self):
        """
        POSTメソッドにおいてfollows=unfollowなら、
        ログインユーザーはそのプロフィールのユーザーを
        アンフォローする。
        """
        self.client.post(self.url, data=dict(follows='unfollow'))
        self.assertEqual(Follows.objects.filter(actor=self.user, followed_user=self.tar_user), [])
