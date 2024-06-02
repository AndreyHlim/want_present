import os

from api.permissions import OnlyAuthorOrAdmin
from dotenv import load_dotenv
from gifts.models import Gift
from holidays.models import Holiday
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from users.models import Profile, Subscribe

from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from .serializers import (
    GiftSerializer,
    HolidaySerializer,
    SubscribeSerializer,
    UserSerializer
)

load_dotenv()

User = get_user_model()


class HolidaysViewSet(viewsets.ModelViewSet):
    queryset = Holiday.objects.all()
    serializer_class = HolidaySerializer
    http_method_names = ['get', 'post', 'delete', 'patch']

    def list(self, request):
        queryset = self.queryset.filter(
            user=request.user.id_telegram
        ).order_by('date')
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)

    def get_permissions(self):
        if self.request.method == 'DELETE' or self.request.method == 'PATCH':
            return (OnlyAuthorOrAdmin(),)
        return (IsAuthenticated(),)

    def create(self, request):
        request.data['user'] = request.user.id_telegram
        serializers = HolidaySerializer(data=request.data)
        if serializers.is_valid():
            serializers.save()
            return Response(serializers.data, status=status.HTTP_201_CREATED)
        return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)


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

    def get_permissions(self):
        if self.request.method == 'GET':
            return (IsAuthenticated(),)
        elif self.request.method == 'POST':
            return (AllowAny(),)
        return (OnlyAuthorOrAdmin(),)

    def create(self, request):
        serializers = self.serializer_class(data=request.data)
        if serializers.is_valid():
            serializers.save()

            # Удалить потом. Пароль будет присваиваться в commands/bot.py
            user = Profile.objects.get(
                id_telegram=serializers.validated_data['id_telegram']
            )
            user.set_password(os.getenv('USER_PASSWORD'))
            user.save()

            return Response(serializers.data, status=status.HTTP_201_CREATED)
        return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=True,
        methods=['get',],
    )
    def holidays(self, request, pk):
        queryset = Holiday.objects.filter(
            user=get_object_or_404(User, id_telegram=pk)
        ).order_by('date')
        serializer = HolidaySerializer(queryset, many=True)
        return Response(serializer.data)


class GiftsViewSet(viewsets.ModelViewSet):
    queryset = Gift.objects.all()
    serializer_class = GiftSerializer
    http_method_names = ['get', 'post', 'delete', 'patch']

    def get_permissions(self):
        if (
            self.request.method == 'DELETE'
            or self.request.method == 'PATCH'
        ):
            return (OnlyAuthorOrAdmin(),)
        return (IsAuthenticated(),)

    def create(self, request):
        request.data.update(
            {
                'user': request.user.id_telegram,
                'is_donated': False,
                'is_booked': False,
                'is_want': True,
            }
        )
        serializers = GiftSerializer(data=request.data)
        if serializers.is_valid():
            serializers.save()
            return Response(serializers.data, status=status.HTTP_201_CREATED)
        return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)
