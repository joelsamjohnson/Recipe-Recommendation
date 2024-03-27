from rest_framework import serializers

class FollowUserSerializer(serializers.Serializer):
    user_id = serializers.IntegerField(help_text="ID of the user to follow")
