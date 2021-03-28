from django.db import models
from django.contrib.auth.models import User

class Follows(models.Model):
    actor = models.ForeignKey(User, related_name="actor", on_delete=models.CASCADE)
    followed_user = models.ForeignKey(User, related_name="followed_user", on_delete=models.CASCADE)

    def __str__(self):
        return "{} : {}".format(self.actor.username, self.followed_user.username)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['actor', 'followed_user'], name='unique_follow')
        ]
