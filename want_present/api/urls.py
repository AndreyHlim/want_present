from rest_framework import routers

from django.urls import include, path

from .views import GiftsViewSet, HolidaysViewSet, UsersViewSet

router_v1 = routers.DefaultRouter()
router_v1.register('holidays', HolidaysViewSet, basename='holidays')
router_v1.register('users', UsersViewSet, basename='users')
router_v1.register('gifts', GiftsViewSet, basename='gifts')

app_name = 'api'

urlpatterns = [
    path('', include(router_v1.urls)),
]
