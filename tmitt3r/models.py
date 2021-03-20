from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Tm33t(models.Model):
    poster = models.ForeignKey(User, on_delete=models.CASCADE)
    post_time = models.DateTimeField(verbose_name='tm33t time', auto_now=True)
    content = models.TextField()

    def __str__(self):
        return self.content
