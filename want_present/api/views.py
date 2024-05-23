from api.permissions import AuthorStaffOrReadOnly
from holidays.models import Holiday
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from users.models import Subscribe

from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from .serializers import HolidaySerializer, SubscribeSerializer, UserSerializer

User = get_user_model()


class HolidaysViewSet(viewsets.ModelViewSet):
    queryset = Holiday.objects.all()
    serializer_class = HolidaySerializer
    http_method_names = ['get', 'post', 'delete', 'patch']

    def list(self, request):
        queryset = self.queryset.filter(user=request.user.id_telegram)
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)

    def get_permissions(self):
        if self.request.method == 'DELETE' or self.request.method == 'PATCH':
            return (AuthorStaffOrReadOnly(),)
        return (IsAuthenticated(),)


class UsersViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    http_method_names = ['get', 'post', 'delete', 'patch',]
    serializer_class = UserSerializer

    @action(
        detail=True,
        methods=['post',],
    )
    def favorite(self, request, pk):
        if request.data['user'] == int(pk):
            return Response(
                {'errors': 'Нельзя подписаться на себя!'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        request.data['subscribe'] = pk
        serializers = SubscribeSerializer(data=request.data)
        if serializers.is_valid():
            serializers.save()
            return Response(serializers.data, status=status.HTTP_201_CREATED)
        return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)

    @favorite.mapping.delete
    def delete_favorite(self, request, pk):
        subscribe = get_object_or_404(
            Subscribe, user=request.data['user'], subscribe=pk,
        )
        subscribe.delete()
        return Response("Подписка удалена", status=status.HTTP_204_NO_CONTENT)
