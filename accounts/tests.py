from django.test import TestCase
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from django.db.utils import IntegrityError
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.conf import settings
from .models import Follows


sample_password = 'SamplePassword'
def create_userdata(username, password=sample_password):
    return {'username': username, 'password1': password, 'password2': password}


class UserCreationFormTests(TestCase):
    def test_username_clean_success(self):
        """
        usernameがデータベース上に無く、入力が想定された文字種
        の範囲内かつ、再入力したパスワードが一致すれば
        is_validはTrueを返す
        """
        data = create_userdata('Sample1')
        form = UserCreationForm(data=data)
        self.assertTrue(form.is_valid)

    def test_username_clean_already_has_fail(self):
        """
        入力値自体が正しい範囲内にあっても、
        もし入力されたusernameがすでに存在すれば、
        UserCreationFormクラスはValidationErrorを返す
        """
        username='AlreadyHasSample'
        User.objects.create(username=username)
        data = (create_userdata(username))
        form = UserCreationForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertRaisesMessage(ValidationError, '同じユーザー名が既に登録済みです。')


class SignUpViewTests(TestCase):
    def test_add_User(self):
        """
        SignUpViewクラスはSignUpが成功すると、tmitt3r:homeに
        ログイン状態でリダイレクトし、Userにそのアカウントが追加される。
        """
        url = reverse('accounts:signup')
        data = create_userdata('Ken')
        response = self.client.post(url, data=data)
        self.assertRedirects(response, reverse('tmitt3r:home'))
        self.assertTrue(User.objects.filter(username='Ken').exists())


class LoginViewTests(TestCase):
    def setUp(self):
        self.username = 'Sample2'
        self.password = sample_password
        User.objects.create_user(username=self.username, password=self.password)
        self.userdata = {'username': self.username, 'password': self.password}
        self.url = reverse('accounts:login')

    def test_user_login(self):
        """
        getメソッドに対しては、formをcontextとして与えた状態で同じページを返す。
        """
        response = self.client.get(self.url)
        self.assertTrue(isinstance(response.context['form'], AuthenticationForm))

    def test_user_login_post(self):
        """
        正しい情報を持ったpostメソッドに対しては、
        認証された後nextが与えられていなければ、
        setting.LOGIN_REDIRECT_URLにリダイレクトされる。
        """
        data = self.userdata
        response = self.client.post(self.url, data=self.userdata)
        self.assertRedirects(response, reverse(settings.LOGIN_REDIRECT_URL))


class LogoutViewTests(TestCase):
    def setUp(self):
        self.username = 'LogoutTestUser'
        self.password = sample_password
        User.objects.create_user(username=self.username, password=self.password)
    
    def test_user_logout(self):
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(reverse('accounts:logout'))
        self.assertRedirects(response, reverse(settings.LOGOUT_REDIRECT_URL))


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


class FollowsFeatureTests(TestCase):
    def setUp(self):
        self.username = 'UserDetailViewTest'
        self.password = 'SamplePassword'
        self.user = User.objects.create_user(username=self.username, password=self.password)
        self.tar_user = User.objects.create_user(username='UDVTest')
        self.client.login(username=self.username, password=self.password)
        self.follow_url = reverse('accounts:follow')
        self.unfollow_url = reverse('accounts:unfollow')

    def test_follow_post(self):
        """
        followページに有効なusernameを与えると
        そのユーザーをフォローする
        """
        self.client.post(self.follow_url, data={'username': str(self.tar_user)})
        self.assertTrue(Follows.objects.filter(actor=self.user, followed_user=self.tar_user).exists())

    def test_unfollow_post(self):
        """
        unfollowページに有効なusernameを与えると
        そのユーザーをアンフォローする。
        """
        if not Follows.objects.filter(actor=self.user, followed_user=self.tar_user).exists():
            Follows.objects.create(actor=self.user, followed_user=self.tar_user)
        self.client.post(self.unfollow_url, data={'username': str(self.tar_user)})
        self.assertFalse(Follows.objects.filter(actor=self.user, followed_user=self.tar_user).exists())

    def test_follow_yourself_fail(self):
        """
        自分自身をフォローすることはできない。
        """
        own_url = reverse('accounts:profile', kwargs={'pk': self.user.pk})
        self.client.post(own_url, data={'username': str(self.user)})
        self.assertFalse(Follows.objects.filter(actor=self.user, followed_user=self.user).exists())
