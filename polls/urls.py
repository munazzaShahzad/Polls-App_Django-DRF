from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (UserLoginAPIView, UserRegisterAPIView, UserLogoutAPIView,
                    PollAPIView, ChoiceAPIView, TagAPIView, CategoryAPIView,
                    ProfileAPIView, GroupAPIView, VoteAPIView, PollResultsAPIView,
                    ChangePasswordAPIView, UserSelfUpdateAPIView, PasswordResetRequestAPIView,
                    PasswordResetAPIView)

app_name = "polls"

urlpatterns = [
    # Profile
    path('', ProfileAPIView.as_view(), name='user-profile'),

    # Authentication
    path('auth/login/', UserLoginAPIView.as_view(), name='user-login'),
    path('auth/register/', UserRegisterAPIView.as_view(), name='user-register'),
    path('auth/logout/', UserLogoutAPIView.as_view(), name='user-logout'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='user-refresh-access'),
    path('auth/change_password/', ChangePasswordAPIView.as_view(), name='user-change-password'),
    path('auth/user_update/', UserSelfUpdateAPIView.as_view(), name='user-self-update'),

    # Password reset request
    path('auth/password/reset/', PasswordResetRequestAPIView.as_view(), name='password_reset_request'),
    # Password reset confirmation
    path('auth/password/reset/confirm/<str:uidb64>/<str:token>/', PasswordResetAPIView.as_view(),
         name='password_reset_confirm'),

    # Polls
    path('polls/', PollAPIView.as_view(), name='poll-list-create'),
    path('polls/<int:pk>/', PollAPIView.as_view(), name='poll-detail'),

    # Vote
    path('vote/<int:poll_id>/', VoteAPIView.as_view(), name='vote-poll'),

    # Closed Polls Results
    path('poll_results/', PollResultsAPIView.as_view(), name='poll-results'),

    # Choices
    path('choices/', ChoiceAPIView.as_view(), name='choice-list-create'),
    path('choices/<int:pk>/', ChoiceAPIView.as_view(), name='choice-detail'),

    # Tags
    path('tags/', TagAPIView.as_view(), name='tag-list-create'),
    path('tags/<int:pk>/', TagAPIView.as_view(), name='tag-detail'),

    # Categories
    path('categories/', CategoryAPIView.as_view(), name='category-list-create'),
    path('categories/<int:pk>/', CategoryAPIView.as_view(), name='category-detail'),

    # Groups
    path('groups/', GroupAPIView.as_view(), name='group-list'),
    path('groups/<int:pk>/', GroupAPIView.as_view(), name='group-detail'),
]
