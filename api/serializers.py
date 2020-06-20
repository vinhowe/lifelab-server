from rest_framework import serializers
from rest_framework.relations import HyperlinkedIdentityField
from rest_framework_nested.relations import (
    NestedHyperlinkedRelatedField,
    NestedHyperlinkedIdentityField,
)

from api.models import Issue, Lab, IssueComment


class LabSerializer(serializers.HyperlinkedModelSerializer):
    issues = HyperlinkedIdentityField(
        view_name="issues-list", lookup_url_kwarg="lab_pk", lookup_field="pk"
    )

    class Meta:
        model = Lab
        fields = ["id", "url", "issues", "experiments"]


class IssueSerializer(serializers.HyperlinkedModelSerializer):
    comments = NestedHyperlinkedIdentityField(
        view_name="issue-comments-list",
        parent_lookup_kwargs={"lab_pk": "lab__pk"},
        lookup_url_kwarg="issue_number",
    )
    url = NestedHyperlinkedIdentityField(
        view_name="issues-detail",
        parent_lookup_kwargs={"lab_pk": "lab__pk"},
        lookup_field="number",
    )

    def create(self, validated_data):
        context_kwargs = self.context["view"].kwargs
        lab = Lab.objects.get(pk=context_kwargs["lab_pk"])
        instance = Issue.objects.create(
            **validated_data, lab=lab
        )
        # instance.issue =
        return instance

    class Meta:
        model = Issue
        fields = [
            "number",
            "id",
            "url",
            "state",
            "title",
            "description",
            "comments",
            "lab",
            "deleted",
        ]
        read_only_fields = ["lab"]


class IssueCommentSerializer(serializers.HyperlinkedModelSerializer):
    issue = NestedHyperlinkedRelatedField(
        view_name="issues-detail",
        read_only=True,
        parent_lookup_kwargs={"lab_pk": "lab__pk"},
        lookup_url_kwarg="number",
    )

    url = NestedHyperlinkedIdentityField(
        view_name="issue-comments-detail",
        parent_lookup_kwargs={
            "lab_pk": "issue__lab__pk",
            "issue_number": "issue__number",
        },
    )

    def create(self, validated_data):
        context_kwargs = self.context["view"].kwargs
        issue = Issue.objects.get(
            lab=context_kwargs["lab_pk"], number=context_kwargs["issue_number"]
        )
        instance = IssueComment.objects.create(**validated_data, issue=issue)
        # instance.issue =
        return instance

    class Meta:
        model = IssueComment
        fields = ["id", "url", "issue", "body", "created", "deleted"]
        read_only_fields = ["created"]
