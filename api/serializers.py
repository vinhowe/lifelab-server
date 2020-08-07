from typing import List, Dict

from rest_framework import serializers
from rest_framework.relations import HyperlinkedIdentityField, HyperlinkedRelatedField
from rest_framework_nested.relations import (
    NestedHyperlinkedRelatedField,
    NestedHyperlinkedIdentityField,
)

from api.models import (
    Issue,
    Lab,
    IssueComment,
    MAX_BODY_TEXT_LENGTH,
    Experiment,
    CheckIn,
    OPEN,
)


class IssueIdListField(serializers.Field):
    def to_representation(self, value) -> List:
        queue_list = (
            []
            if not value.queue_order
            else [int(x) for x in value.queue_order.split(",")]
        )
        open_issue_ids = [
            issue.id
            for issue in Issue.objects.filter(
                lab__pk=value.pk, state=OPEN, deleted=False
            )
        ]
        updated_list = []

        for id in queue_list:
            if id in open_issue_ids:
                # If id is in open_issue_ids, then we don't want to add it again
                open_issue_ids.remove(id)
                updated_list.append(id)

        # open_issue_ids is now only open issue IDs that aren't in queue_list
        updated_list.extend(open_issue_ids)

        if queue_list != updated_list:
            value.queue_order = ",".join([str(x) for x in updated_list])
            value.save()

        return updated_list

    def to_internal_value(self, data) -> Dict[str, str]:
        internal_value = None
        if isinstance(data, list):
            internal_value = ",".join([str(x) for x in data])
        elif isinstance(data, str):
            internal_value = data[1:-1].replace(" ", "")

        return {"queue_order": internal_value}


class LabSerializer(serializers.HyperlinkedModelSerializer):
    issues = HyperlinkedIdentityField(
        view_name="issues-list", lookup_url_kwarg="lab_pk", lookup_field="pk"
    )
    experiments = HyperlinkedIdentityField(
        view_name="experiments-list", lookup_url_kwarg="lab_pk", lookup_field="pk"
    )
    check_ins = HyperlinkedIdentityField(
        view_name="check-ins-list", lookup_url_kwarg="lab_pk", lookup_field="pk"
    )
    queue = IssueIdListField(source="*")

    class Meta:
        model = Lab
        fields = ["id", "url", "issues", "experiments", "check_ins", "queue"]


class ExperimentSerializer(serializers.HyperlinkedModelSerializer):
    url = NestedHyperlinkedIdentityField(
        view_name="experiments-detail",
        parent_lookup_kwargs={"lab_pk": "lab__pk"},
        lookup_field="number",
    )
    description = serializers.CharField(
        max_length=MAX_BODY_TEXT_LENGTH, allow_blank=True, required=False
    )
    terms = serializers.CharField(
        max_length=MAX_BODY_TEXT_LENGTH, allow_blank=True, required=False
    )

    def create(self, validated_data):
        context_kwargs = self.context["view"].kwargs
        lab = Lab.objects.get(pk=context_kwargs["lab_pk"])
        instance = Experiment.objects.create(**validated_data, lab=lab)
        return instance

    class Meta:
        model = Experiment
        fields = [
            "number",
            "id",
            "url",
            "state",
            "title",
            "description",
            "terms",
            "created",
            "end_date",
            "lab",
            "deleted",
        ]
        read_only_fields = ["lab", "created"]


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
    description = serializers.CharField(
        max_length=MAX_BODY_TEXT_LENGTH, allow_blank=True, required=False
    )
    experiments = NestedHyperlinkedRelatedField(
        many=True,
        queryset=Experiment.objects.all(),
        view_name="experiments-detail",
        parent_lookup_kwargs={"lab_pk": "lab__pk"},
        lookup_url_kwarg="number",
        lookup_field="number",
        required=False,
    )

    def create(self, validated_data):
        context_kwargs = self.context["view"].kwargs
        lab = Lab.objects.get(pk=context_kwargs["lab_pk"])
        instance = Issue.objects.create(**validated_data, lab=lab)
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
            "experiments",
            "created",
            "comments",
            "lab",
            "deleted",
        ]
        read_only_fields = ["lab", "created"]


class CheckInSerializer(serializers.HyperlinkedModelSerializer):
    url = NestedHyperlinkedIdentityField(
        view_name="check-ins-detail",
        parent_lookup_kwargs={"lab_pk": "lab__pk"},
        lookup_field="number",
    )
    retrospective = serializers.CharField(
        max_length=MAX_BODY_TEXT_LENGTH, allow_blank=True, required=False
    )
    experiments = NestedHyperlinkedRelatedField(
        many=True,
        queryset=Experiment.objects.all(),
        view_name="experiments-detail",
        parent_lookup_kwargs={"lab_pk": "lab__pk"},
        lookup_url_kwarg="number",
        lookup_field="number",
        required=False,
    )

    def create(self, validated_data) -> CheckIn:
        context_kwargs = self.context["view"].kwargs
        lab = Lab.objects.get(pk=context_kwargs["lab_pk"])
        instance = CheckIn.objects.create(**validated_data, lab=lab)
        instance.experiments.set(
            Experiment.objects.filter(
                lab__pk=context_kwargs["lab_pk"], deleted=False, state="ACTIVE",
            )
        )
        return instance

    class Meta:
        model = CheckIn
        fields = [
            "number",
            "id",
            "url",
            "complete",
            "retrospective",
            "experiments",
            "created",
            "lab",
            "deleted",
        ]
        read_only_fields = ["lab", "created"]


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
