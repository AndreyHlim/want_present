from rest_framework import status, viewsets
from holidays.models import Holiday
from users.models import Subscribe
from .serializers import HolidaySerializer, UserSerializer, SubscribeSerializer
from django.contrib.auth import get_user_model
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404


User = get_user_model()


class HolidaysViewSet(viewsets.ModelViewSet):
    queryset = Holiday.objects.all()
    serializer_class = HolidaySerializer


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
