from django.test import TestCase, override_settings
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from .models import Tm33t
import time

no_csrf_middleware = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

password = 'SamplePassword'

def create_user_by_id(obj, id):
    username = obj.__class__.__name__ + str(id)
    user = User.objects.create_user(username=username, password=password)
    return user

def create_text(obj, id):
    return 'This is ' + obj.__class__.__name__ + str(id) + ' Sample Text.'


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


class Tm33tModelTests(TestCase):
    def test_has_been_liked(self):
        """
        has_been_liked メソッドのテスト
        引数にはUserオブジェクトかusernameを取り、
        users_likedに含まれていればTrueを返す。
        """
        u1 = User.objects.create_user(username='Tm33tModelTests1')
        u2 = User.objects.create_user(username='Tm33tModelTests2')
        u3 = User.objects.create_user(username='Tm33tModelTest3')
        t1 = Tm33t.objects.create(poster=u1, content='test_has_been_liked')
        t1.users_liked.add(u2)
        self.assertTrue(t1.has_been_liked(u2))
        self.assertFalse(t1.has_been_liked(u3))
        self.assertTrue(t1.has_been_liked(u2.get_username()))
        self.assertFalse(t1.has_been_liked(u3.get_username()))
        t1.users_liked.remove(u2)
        self.assertFalse(t1.has_been_liked(u2))


@override_settings(MIDDLEWARE=no_csrf_middleware)
class Tm33tLikeFeatureTests(TestCase):
    def setUp(self):
        # create users
        self.user = create_user_by_id(self, 'User')
        self.poster = create_user_by_id(self, 'Poster')
        # create target tm33t
        self.text1 = create_text(self, 1)
        self.text2 = create_text(self, 2)
        self.tm33t1 = Tm33t.objects.create(poster=self.poster, content=self.text1)
        self.tm33t2 = Tm33t.objects.create(poster=self.poster, content=self.text2)
        # user login
        self.client.login(username=self.user.username, password=password)
        # post target url
        self.tm33t1_url = reverse('tmitt3r:detail', kwargs={'pk': self.tm33t1.pk})
        self.tm33t2_url = reverse('tmitt3r:detail', kwargs={'pk': self.tm33t2.pk})

    def test_like_post(self):
        """
        Tm33tDetailViewのURLにpostメソッドで適切なデータを与えると
        そのユーザーが対象のツイートにライクする。
        """
        self.client.post(self.tm33t1_url, data={'like': 'like', 'pk': self.tm33t1.pk})
        self.assertTrue(self.tm33t1.users_liked.filter(username=self.user.username).exists())

    def test_like_post(self):
        """
        Tm33tDetailViewのURLにpostメソッドで適切なデータを与えると
        そのユーザーが対象のツイートのライクを外す。
        """
        self.tm33t2.users_liked.add(self.user)
        self.assertTrue(self.tm33t2.users_liked.filter(username=self.user.username).exists())
        # tm33t2に対するUnlike
        self.client.post(self.tm33t2_url, data={'like': 'unlike', 'pk': self.tm33t2.pk})
        self.assertFalse(self.tm33t2.users_liked.filter(username=self.user.username).exists())
