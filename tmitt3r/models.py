from django.db import models
from django.contrib.auth.models import User

class Tm33t(models.Model):
    poster = models.ForeignKey(User, related_name='tm33ts', on_delete=models.CASCADE)
    post_time = models.DateTimeField(verbose_name='tm33t time', auto_now=True)
    content = models.TextField(null=True)
    users_liked = models.ManyToManyField(User, related_name='tm33ts_liked')

    def __str__(self):
        length = (len(self.content) - 1) if (len(self.content) < 20) else 18
        return repr(self.content[:length])

    def has_been_liked(self, user):
        if isinstance(user, User):
            return self.users_liked.filter(username=user.get_username()).exists()
        return self.users_liked.filter(username=user).exists()
    
    def is_reply(self):
        return hasattr(self, 'reply')

    def is_retm33t(self):
        return hasattr(self, 'retm33t')


class Reply(Tm33t):
    related_tm33t = models.ForeignKey(Tm33t, related_name="replies", on_delete=models.CASCADE)


class Retm33t(Tm33t):
    tm33t_retm33ted = models.ForeignKey(Tm33t, related_name="retm33ts", on_delete=models.CASCADE)
