from rest_framework import viewsets

from api.models import Issue, Lab, IssueComment, Experiment
from api.serializers import (
    IssueSerializer,
    LabSerializer,
    IssueCommentSerializer, ExperimentSerializer,
)


class LabViewSet(viewsets.ModelViewSet):
    queryset = Lab.objects.all()
    serializer_class = LabSerializer
    pagination_class = None


class LabIssueViewSet(viewsets.ModelViewSet):
    def get_queryset(self):
        return Issue.objects.filter(lab=self.kwargs["lab_pk"], deleted=False)

    lookup_field = "number"
    serializer_class = IssueSerializer
    pagination_class = None


class LabExperimentViewSet(viewsets.ModelViewSet):
    def get_queryset(self):
        return Experiment.objects.filter(lab=self.kwargs["lab_pk"], deleted=False)

    lookup_field = "number"
    serializer_class = ExperimentSerializer
    pagination_class = None


class IssueCommentViewSet(viewsets.ModelViewSet):
    def get_queryset(self):
        return IssueComment.objects.filter(
            issue__lab=self.kwargs["lab_pk"],
            issue=self.kwargs["issue_number"]
        )

    serializer_class = IssueCommentSerializer
    pagination_class = None
