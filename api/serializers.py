from django.contrib.auth.models import User, Group
from rest_framework import serializers

from api.models import Issue, Lab, IssueComment


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ["url", "username", "email", "groups"]


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ["url", "name"]


class LabSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Lab
        fields = ["id", "issues", "experiments"]


class IssueCommentSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = IssueComment
        fields = [
            "id", "history", "issue", "body"
        ]


class IssueSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Issue
        fields = [
            "id",
            "state",
            "number",
            "title",
            "lab",
            "description",
            "deleted",
            # "comments",
        ]
