from django.test import TestCase, override_settings
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from .models import Tm33t

no_csrf_middleware = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Create your tests here.
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
        self.assertEqual(str(tm33t), text)
