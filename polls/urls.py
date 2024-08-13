from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (UserLoginAPIView, UserRegisterAPIView, UserLogoutAPIView,
                    PollAPIView, ChoiceAPIView, TagAPIView, CategoryAPIView,
                    ProfileAPIView, UserAPIView, GroupAPIView)

app_name = "polls"

urlpatterns = [
    # Profile
    path('', ProfileAPIView.as_view(), name='user-profile'),

    # Authentication
    path('auth/login/', UserLoginAPIView.as_view(), name='user-login'),
    path('auth/register/', UserRegisterAPIView.as_view(), name='user-register'),
    path('auth/logout/', UserLogoutAPIView.as_view(), name='user-logout'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='user-refresh-access'),

    # Polls
    path('polls/', PollAPIView.as_view(), name='poll-list-create'),
    path('polls/<int:pk>/', PollAPIView.as_view(), name='poll-detail'),

    # Choices
    path('choices/', ChoiceAPIView.as_view(), name='choice-list-create'),
    path('choices/<int:pk>/', ChoiceAPIView.as_view(), name='choice-detail'),

    # Tags
    path('tags/', TagAPIView.as_view(), name='tag-list-create'),
    path('tags/<int:pk>/', TagAPIView.as_view(), name='tag-detail'),

    # Categories
    path('categories/', CategoryAPIView.as_view(), name='category-list-create'),
    path('categories/<int:pk>/', CategoryAPIView.as_view(), name='category-detail'),

    # Users
    path('users/', UserAPIView.as_view(), name='user-list'),
    path('users/<int:pk>/', UserAPIView.as_view(), name='user-detail'),

    # Groups
    path('groups/', GroupAPIView.as_view(), name='group-list'),
    path('groups/<int:pk>/', GroupAPIView.as_view(), name='group-detail'),
]
