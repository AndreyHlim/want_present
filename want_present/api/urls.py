from rest_framework import routers
from .views import HolidaysViewSet, UsersViewSet
from django.urls import include, path


router_v1 = routers.DefaultRouter()
router_v1.register('holidays', HolidaysViewSet, basename='holidays')
router_v1.register('users', UsersViewSet, basename='users')

urlpatterns = [
    path('', include(router_v1.urls)),
]
