from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from django.template import Context, Template
from .models import Tm33t, Reply, Retm33t
import json


PASSWORD = 'SamplePassword'

def create_user_by_id(obj, id):
    username = obj.__class__.__name__ + str(id)
    user = User.objects.create_user(username=username, password=PASSWORD)
    return user

def create_text(obj, id):
    return 'This is ' + obj.__class__.__name__ + str(id) + ' Sample Text.'

# class based view tests
class HomeViewTests(TestCase):
    def setUp(self):
        username = 'HomeViewTest'
        self.user = User.objects.create_user(username=username, 
                                             password=PASSWORD)
        self.client.login(username=username, password=PASSWORD)
        self.text_list = []
        for i in range(10):
            text = 'This is HomeViewTest Tm33t text No.{}.'.format(i)
            Tm33t.objects.create(poster=self.user, content=text)
            self.text_list.append(text)
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
            self.assertTrue(queryset[i].content in self.text_list)


class Tm33tViewTests(TestCase):
    def setUp(self):
        self.username = 'Tm33tViewTest'
        self.url = reverse('tmitt3r:tm33t')
        self.user = User.objects.create_user(username=self.username,
                                             password=PASSWORD)
        self.client.login(username=self.username, password=PASSWORD)
    
    def test_tm33t(self):
        """
        ツイートが成功するとデータベースに登録され、
        posterは投稿者に、post_timeは投稿時の時間になる。
        """
        text = 'This is sample tm33t for Tm33tViewTest.'
        data = {'content': text}
        time = timezone.now()
        self.client.post(self.url, data=data)
        tm33t = Tm33t.objects.filter(
                            poster__username=self.username
                        ).get(
                            post_time__gte=time
                        )
        self.assertEqual(tm33t.content, text)

    def test_tm33t_with_blank_content(self):
        """
        空白の内容をPOSTリクエストすると、同じ画面に再アクセスさせる。
        """
        res = self.client.post(self.url, data={'content': ""})
        self.assertTemplateUsed(res, 'tmitt3r/tm33t.html')


class Tm33tLikeViewTests(TestCase):
    def setUp(self):
        # Like/UnlikeするUser
        self.user = User.objects.create_user(username='LoginUser', password=PASSWORD)

        # テスト対象のTm33tのposter
        self.poster = User.objects.create_user(username='Tm33tPoster', password=PASSWORD)

        self.tm33t = Tm33t.objects.create(poster=self.poster, content="")

        self.client.login(username=self.user.username, password=PASSWORD)
        self.url = reverse('tmitt3r:like') # post target url

    def test_like_post(self):
        """
        Tm33tDetailViewのURLにpostメソッドでlike='like'と対象ツイートのpkを与えると
        そのユーザーが対象のツイートにライクする。
        """
        res = self.client.post(self.url, data={'like': 'like', 'pk': self.tm33t.pk})
        self.assertEqual(200, res.status_code)
        self.assertTrue(self.tm33t.users_liked.filter(username=self.user.username).exists())

    def test_unlike_post(self):
        """
        Tm33tDetailViewのURLにpostメソッドでlike='unlike'と対象ツイートのpkを与えると
        そのユーザーが対象のツイートのライクを外す。
        """
        self.tm33t.users_liked.add(self.user)
        self.assertTrue(self.tm33t.users_liked.filter(username=self.user.username).exists())

        # tm33tに対するUnlike
        res = self.client.post(self.url, data={'like': 'unlike', 'pk': self.tm33t.pk})
        self.assertEqual(200, res.status_code)
        self.assertFalse(self.tm33t.users_liked.filter(username=self.user.username).exists())
    
    def test_unlike_post(self):
        """
        POSTメソッドでlikeデータを送信しないとJSONの
        {"result" : "Invalid Post Data"} が返る。
        """
        res = self.client.post(self.url, data={'pk': self.tm33t.pk})
        self.assertEqual(200, res.status_code)
        json_decoded_response = json.loads(res.content)
        self.assertEqual(json_decoded_response.get('result'), 'Invalid Post Data')


class Tm33tReplyViewTests(TestCase):
    def setUp(self):
        self.user = create_user_by_id(self, 'User')
        self.tm33t_poster = create_user_by_id(self, 'Tm33tPoster')
        # user login
        self.client.login(username=self.user.username, password=PASSWORD)
        # 元のツイート
        self.tm33t = Tm33t.objects.create(poster=self.tm33t_poster, content=create_text(self, 1))
        self.url = reverse('tmitt3r:reply', kwargs={'pk': self.tm33t.pk})
    
    def test_reply_post(self):
        """
        ReplyをPOSTするとホーム画面にリダイレクトされ、データベースに登録される。
        """
        text = create_text(self, 2)
        redirect_url = reverse('tmitt3r:home')
        res = self.client.post(self.url, data={'content': text})
        self.assertRedirects(res, redirect_url)
        self.assertTrue(Reply.objects.filter(content=text).exists())


class Retm33tViewTests(TestCase):
    def setUp(self):
        self.user = create_user_by_id(self, 'User')
        self.tm33t_poster = create_user_by_id(self, 'Tm33tPoster')
        # user login
        self.client.login(username=self.user.username, password=PASSWORD)
        # 元のツイート
        self.tm33t = Tm33t.objects.create(poster=self.tm33t_poster, content=create_text(self, 1))
        self.url = reverse('tmitt3r:retm33t')
    
    def test_retm33t_post(self):
        """
        Retm33tビューにtm33tのpkをPOSTすると、そのtm33tをRetm33tする。
        """
        res = self.client.post(self.url, data={'pk': self.tm33t.pk})
        self.assertEqual(200, res.status_code)
        self.assertTrue(Retm33t.objects.filter(tm33t_retm33ted=self.tm33t).exists())


class Unretm33tTests(TestCase):
    def setUp(self):
        self.user = create_user_by_id(self, 'User')
        self.tm33t_poster = create_user_by_id(self, 'Tm33tPoster')
        # user login
        self.client.login(username=self.user.username, password=PASSWORD)
        # 元のツイート
        self.tm33t = Tm33t.objects.create(poster=self.tm33t_poster, content=create_text(self, 1))
        self.url = reverse('tmitt3r:unretm33t')
    
    def test_unretm33t_post(self):
        """
        Unretm33tビューにTm33tのpkをPOSTすると、そのTm33tのRetm33tを削除する。
        """
        Retm33t.objects.create(poster=self.user, tm33t_retm33ted=self.tm33t)
        res = self.client.post(self.url, data={'pk': self.tm33t.pk})
        self.assertEqual(200, res.status_code)
        self.assertFalse(Retm33t.objects.filter(poster=self.user, tm33t_retm33ted=self.tm33t).exists())


# Django custom models tests
class Tm33tModelTests(TestCase):
    def setUp(self):
        self.u1 = User.objects.create_user(username='Tm33tModelTests1')
        self.u2 = User.objects.create_user(username='Tm33tModelTests2')
        self.u3 = User.objects.create_user(username='Tm33tModelTest3')
        self.t1 = Tm33t.objects.create(poster=self.u1, content=create_text(self, 1))

    def test_has_been_liked(self):
        """
        has_been_liked メソッドのテスト
        引数にはUserオブジェクトかusernameを取り、
        users_likedに含まれていればTrueを返す。
        """
        self.t1.users_liked.add(self.u2)
        self.assertTrue(self.t1.has_been_liked(self.u2))
        self.assertFalse(self.t1.has_been_liked(self.u3))
        self.assertTrue(self.t1.has_been_liked(self.u2.get_username()))
        self.assertFalse(self.t1.has_been_liked(self.u3.get_username()))
        self.t1.users_liked.remove(self.u2)
        self.assertFalse(self.t1.has_been_liked(self.u2))
    
    def test_is_reply(self):
        """
        Tm33tオブジェクトがReplyに継承されたものである場合に
        is_reply() はTrueを返す
        """
        text = create_text(self, 2)
        # Replyオブジェクトとして作成
        reply = Reply.objects.create(poster=self.u1, related_tm33t=self.t1, content=text)
        # tm33tオブジェクトとして取得
        tm33t = Tm33t.objects.get(content=text)
        self.assertTrue(reply.is_reply())
        self.assertTrue(tm33t.is_reply())
    
    def test_is_not_reply(self):
        """
        Tm33tオブジェクトがReplyでない場合には
        is_reply()はFalseを返す
        """
        self.assertFalse(self.t1.is_reply())
    
    def test_is_retm33t(self):
        """
        Tm33tオブジェクトがRetm33tに継承されたものである場合に
        is_retm33t() はTrueを返す
        """
        text = create_text(self, 3)
        # Replyオブジェクトとして作成
        retm33t = Retm33t.objects.create(poster=self.u1, tm33t_retm33ted=self.t1, content=text)
        # tm33tオブジェクトとして取得
        tm33t = Tm33t.objects.get(content=text)
        self.assertTrue(retm33t.is_retm33t())
        self.assertTrue(tm33t.is_retm33t())
    
    def test_is_not_retm33t(self):
        """
        Tm33tオブジェクトがRetm33tでない場合には
        is_retm33t()はFalseを返す
        """
        self.assertFalse(self.t1.is_retm33t())


# Custom template tag tests
class Retm33tStateTemplateTagTests(TestCase):
    def setUp(self):
        self.user = create_user_by_id(self, 'User')
        self.client.login(username=self.user.username, password=PASSWORD)
        self.poster = create_user_by_id(self, 'Poster')
        self.tm33t = Tm33t.objects.create(poster=self.poster) # 使うtm33t
    
    def test_retm33t_state_rendering(self):
        """
        ユーザーがretm33tしたtm33tに対しては、retm33t_stateテンプレートタグは
        retm33tedという文字列を返す
        """
        Retm33t.objects.create(poster=self.user, tm33t_retm33ted=self.tm33t)
        context = Context({'tm33t': self.tm33t, 'user': self.user})
        template_to_render = Template(
            '{% load tm33t_state %}'
            '{% retm33t_state tm33t user %}'
        )
        rendered_template = template_to_render.render(context)
        self.assertInHTML('retm33ted', rendered_template)
    
    def test_retm33t_state_rendering(self):
        """
        ユーザーがretm33tしていないtm33tに対しては、retm33t_stateテンプレートタグは
        unretm33tedという文字列を返す
        """
        Retm33t.objects.filter(poster=self.user, tm33t_retm33ted=self.tm33t).delete()
        context = Context({'tm33t': self.tm33t, 'user': self.user})
        template_to_render = Template(
            '{% load tm33t_state %}'
            '{% retm33t_state tm33t user %}'
        )
        rendered_template = template_to_render.render(context)
        self.assertInHTML('unretm33ted', rendered_template)


class LikeStateTemplateTagTests(TestCase):
    def setUp(self):
        self.user = create_user_by_id(self, 'User')
        self.client.login(username=self.user.username, password=PASSWORD)
        self.poster = create_user_by_id(self, 'Poster')
    
    def test_like_state_rendering(self):
        """
        ユーザーがlikeしたtm33tに対しては、like_stateテンプレートタグは
        likeという文字列を返す
        """
        tm33t = Tm33t.objects.create(poster=self.poster) # likeされたtm33t
        tm33t.users_liked.add(self.user)
        context = Context({'tm33t': tm33t, 'user': self.user})
        template_to_render = Template(
            '{% load tm33t_state %}'
            '{% like_state tm33t user %}'
        )
        rendered_template = template_to_render.render(context)
        self.assertInHTML('like', rendered_template)
    
    def test_unlike_state_rendering(self):
        """
        ユーザーがlikeしていないtm33tに対しては、like_stateテンプレートタグは
        unlikeという文字列を返す
        """
        tm33t = Tm33t.objects.create(poster=self.poster) # unlikeなtm33t
        context = Context({'tm33t': tm33t, 'user': self.user})
        template_to_render = Template(
            '{% load tm33t_state %}'
            '{% like_state tm33t user %}'
        )
        rendered_template = template_to_render.render(context)
        self.assertInHTML('unlike', rendered_template)
