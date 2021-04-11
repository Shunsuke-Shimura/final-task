from django.db import models
from django.contrib.auth.models import User
from django.db.models.fields import related

class Tm33t(models.Model):
    poster = models.ForeignKey(User, related_name='tm33ts', on_delete=models.CASCADE)
    post_time = models.DateTimeField(verbose_name='tm33t time', auto_now=True)
    content = models.TextField()
    users_liked = models.ManyToManyField(User, related_name='tm33ts_liked')
    users_retm33ted = models.ManyToManyField(User, through='Retm33t')

    def __str__(self):
        length = (len(self.content) - 1) if (len(self.content) < 20) else 18
        return repr(self.content[:length])

    def has_been_liked(self, user):
        if isinstance(user, User):
            return self.users_liked.filter(username=user.get_username()).exists()
        return self.users_liked.filter(username=user).exists()

    def has_been_retm33ted(self, user):
        if isinstance(user, User):
            return self.users_retm33ted.filter(username=user.get_username()).exists()
        return self.users_retm33ted.filter(username=user).exists()
    
    def is_reply(self):
        return hasattr(self, 'reply')


class Reply(Tm33t):
    related_tm33t = models.ForeignKey(Tm33t, related_name="replies", on_delete=models.CASCADE)


class Retm33t(models.Model):
    related_tm33t = models.ForeignKey(Tm33t, on_delete=models.CASCADE)
    user_retm33ted = models.ForeignKey(User, on_delete=models.CASCADE)
    time_retm33ted = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user_retm33ted', 'related_tm33t'], name='unique_retm33t')
        ]
