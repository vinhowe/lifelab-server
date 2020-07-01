"""lifelab_server URL Configuration
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers

from api import views
from api.views import LabIssueViewSet, IssueCommentViewSet, LabExperimentViewSet, \
    LabCheckInViewSet

API_BASE = "api/dev/"

router = DefaultRouter()
router.register("labs", views.LabViewSet)

labs_router = routers.NestedSimpleRouter(router, "labs", lookup="lab")
labs_router.register("issues", LabIssueViewSet, basename="issues")
labs_router.register("experiments", LabExperimentViewSet, basename="experiments")
labs_router.register("check-ins", LabCheckInViewSet, basename="check-ins")

issues_router = routers.NestedSimpleRouter(labs_router, "issues", lookup="issue")
issues_router.register("comments", IssueCommentViewSet, basename="issue-comments")


urlpatterns = [
    path("admin/", admin.site.urls),
    path(API_BASE, include(router.urls)),
    path(API_BASE, include(labs_router.urls)),
    path(API_BASE, include(issues_router.urls)),
    path("api-auth/", include("rest_framework.urls", namespace="rest_framework")),
    ]
