"""lifelab_server URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from rest_framework_extensions.routers import NestedRouterMixin

from api import views
from api.views import IssueCommentViewSet


class NestedDefaultRouter(NestedRouterMixin, routers.DefaultRouter):
    pass


router = NestedDefaultRouter()
router.register("users", views.UserViewSet)
router.register("groups", views.GroupViewSet)
issues_router = router.register("issues", views.IssueViewSet)
issues_router.register(
    "comments",
    IssueCommentViewSet,
    basename="issue-comments",
    parents_query_lookups=["issue"],
)
router.register("labs", views.LabViewSet)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/dev/", include(router.urls)),
    path("api-auth/", include("rest_framework.urls", namespace="rest_framework")),
]
