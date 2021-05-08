from rest_framework import serializers
from accounts.models import Follows

class FollowsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Follows
        fields = ['id', 'actor','followed_user']
        read_only_fields = ['id', 'actor']
