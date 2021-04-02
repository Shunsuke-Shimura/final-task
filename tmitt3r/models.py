from django.db import models
from django.contrib.auth.models import User

class Tm33t(models.Model):
    poster = models.ForeignKey(User, related_name='tm33ts', on_delete=models.CASCADE)
    post_time = models.DateTimeField(verbose_name='tm33t time', auto_now=True)
    content = models.TextField()
    users_liked = models.ManyToManyField(User, related_name='tm33ts_liked')

    def __str__(self):
        length = (len(self.content) - 1) if (len(self.content) < 20) else 18
        return repr(self.content[:length])
