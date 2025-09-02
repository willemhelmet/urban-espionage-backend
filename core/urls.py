from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    GameViewSet, PlayerViewSet, EventViewSet,
    ZoneViewSet, ItemSpawnViewSet, TaskViewSet
)

router = DefaultRouter()
router.register(r'games', GameViewSet, basename='game')
router.register(r'players', PlayerViewSet, basename='player')
router.register(r'events', EventViewSet, basename='event')
router.register(r'zones', ZoneViewSet, basename='zone')
router.register(r'items', ItemSpawnViewSet, basename='item')
router.register(r'tasks', TaskViewSet, basename='task')

urlpatterns = [
    path('api/', include(router.urls)),
]
