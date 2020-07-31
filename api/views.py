from datetime import datetime
from typing import List

from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.settings import api_settings

from api.models import Issue, Lab, IssueComment, Experiment, CheckIn
from api.serializers import (
    IssueSerializer,
    LabSerializer,
    IssueCommentSerializer,
    ExperimentSerializer,
    CheckInSerializer,
)


class ArchiveDeleteMixin:
    def perform_destroy(self, instance) -> None:
        instance.deleted = True
        instance.save()


class LabViewSet(viewsets.ModelViewSet):
    queryset = Lab.objects.all()
    serializer_class = LabSerializer
    pagination_class = None


class LabIssueViewSet(ArchiveDeleteMixin, viewsets.ModelViewSet):
    def get_queryset(self):
        return Issue.objects.filter(lab=self.kwargs["lab_pk"], deleted=False)

    lookup_field = "number"
    serializer_class = IssueSerializer
    pagination_class = None


class LabExperimentViewSet(ArchiveDeleteMixin, viewsets.ModelViewSet):
    def get_queryset(self):
        return Experiment.objects.filter(lab=self.kwargs["lab_pk"], deleted=False)

    lookup_field = "number"
    serializer_class = ExperimentSerializer
    pagination_class = None


class LabCheckInViewSet(
    ArchiveDeleteMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    def get_queryset(self) -> List[CheckIn]:
        return CheckIn.objects.filter(lab=self.kwargs["lab_pk"], deleted=False)

    lookup_field = "number"
    serializer_class = CheckInSerializer
    pagination_class = None

    @action(detail=False, methods=["get", "put", "options", "patch", "delete"])
    def today(self, request, *args, **kwargs) -> Response:
        instances = CheckIn.objects.filter(
            created__date=datetime.today().date(), deleted=False
        )
        instance = instances[0] if len(instances) > 0 else None

        if request.method == "GET":
            if instance:
                serializer = self.get_serializer(instance)
                return Response(serializer.data)
            else:
                serializer = self.get_serializer(data={})
                serializer.is_valid(raise_exception=True)
                serializer.save()
                headers = self.get_success_headers(serializer.data)
                return Response(
                    serializer.data, status=status.HTTP_201_CREATED, headers=headers
                )

        if request.method == "PUT" or request.method == "PATCH":
            if instance:
                partial = kwargs.pop("partial", False)
                serializer = self.get_serializer(
                    instance, data=request.data, partial=partial
                )
                serializer.is_valid(raise_exception=True)
                self.perform_update(serializer)

                if getattr(instance, "_prefetched_objects_cache", None):
                    # If 'prefetch_related' has been applied to a queryset, we need to
                    # forcibly invalidate the prefetch cache on the instance.
                    instance._prefetched_objects_cache = {}

                return Response(serializer.data)
            else:
                return Response(status=status.HTTP_404_NOT_FOUND)

        if request.method == "DELETE":
            instance.deleted = True
            instance.save()
            return Response(status=status.HTTP_204_NO_CONTENT)

        if request.method == "OPTIONS":
            return Response(status=status.HTTP_200_OK)

    @staticmethod
    def get_success_headers(data) -> dict:
        try:
            return {"Location": str(data[api_settings.URL_FIELD_NAME])}
        except (TypeError, KeyError):
            return {}


class IssueCommentViewSet(viewsets.ModelViewSet):
    def get_queryset(self):
        return IssueComment.objects.filter(
            issue__lab=self.kwargs["lab_pk"], issue=self.kwargs["issue_number"]
        )

    serializer_class = IssueCommentSerializer
    pagination_class = None
