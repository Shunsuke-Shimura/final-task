from django.db import models
from django.contrib.auth.models import User
from django.db.models import fields

# Create your models here.
class Tm33t(models.Model):
    poster = models.ForeignKey(User, on_delete=models.CASCADE)
    post_time = models.DateTimeField(verbose_name='tm33t time', auto_now=True)
    content = models.TextField()

    def __str__(self):
        return self.content[:20]

class FollowRelationship(models.Model):
    actor = models.ForeignKey(User, related_name="actor", on_delete=models.CASCADE)
    followed_user = models.ForeignKey(User, related_name="followed_user", on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['actor', 'followed_user'], name='unique_follow')
        ]
