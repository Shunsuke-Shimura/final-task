from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.test import TestCase
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.conf import settings


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
        リダイレクトし、Userにそのアカウントが追加される。
        """
        url = reverse('accounts:signup')
        data = create_userdata('Ken')
        response = self.client.post(url, data=data)
        self.assertRedirects(response, reverse('accounts:login'))
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
        適切なcsrfトークンを持ち、正しい情報を持った
        postメソッドに対しては、認証された後nextが与えられていなければ
        setting.LOGIN_REDIRECT_URLにリダイレクトされる。
        """
        response = self.client.get(self.url)
        token = str(response.context['csrf_token'])
        data = self.userdata
        data['csrfmiddlewaretoken'] = token
        response = self.client.post(self.url, data)
        self.assertRedirects(response, reverse(settings.LOGIN_REDIRECT_URL))
