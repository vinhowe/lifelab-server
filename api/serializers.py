from django.contrib.auth.models import User, Group
from rest_framework import serializers
from rest_framework.reverse import reverse

from api.models import Issue, Lab, IssueComment


class IssueHyperlink(serializers.HyperlinkedRelatedField):
    # We define these as class attributes, so we don't need to pass them as arguments.
    view_name = "lab-issues-detail"
    queryset = Issue.objects.all()

    def get_url(self, obj, view_name, request, format) -> str:
        url_kwargs = {"lab_id": obj.lab.id, "issue_number": obj.number}
        return reverse(view_name, kwargs=url_kwargs, request=request, format=format)

    def get_object(self, view_name, view_args, view_kwargs) -> Issue:
        lookup_kwargs = {
            "lab__id": view_kwargs["lab_id"],
            "number": view_kwargs["issue_number"],
        }
        return self.get_queryset().get(**lookup_kwargs)


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ["url", "username", "email", "groups"]


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ["url", "name"]


class LabSerializer(serializers.HyperlinkedModelSerializer):
    issues = IssueHyperlink(many=True)

    class Meta:
        model = Lab
        fields = ["id", "issues", "experiments"]


class IssueCommentSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = IssueComment
        fields = ["id", "history", "issue", "body"]


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
