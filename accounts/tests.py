from django.contrib.auth.forms import UserCreationForm, UsernameField
from django.test import TestCase
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.urls import reverse


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
        self.assertRaisesMessage(ValidationError, '同じユーザー名が既に登録済みです。')
        self.assertFalse(form.is_valid())


class SignUpViewTests(TestCase):
    def test_add_User(self):
        """
        SignUpViewクラスはSignUpが成功すると、tmitt3r:homeに
        リダイレクトし、Userにそのアカウントが追加される。
        """
        url = reverse('accounts:signup')
        data = create_userdata('Ken')
        response = self.client.post(url, data=data)
        self.assertRedirects(response, reverse('tmitt3r:home'))
        self.assertTrue(User.objects.filter(username='Ken').exists())
    