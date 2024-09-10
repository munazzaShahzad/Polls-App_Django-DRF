from django.urls import path
from rest_framework.schemas import get_schema_view
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (UserLoginAPIView, UserRegisterAPIView, UserLogoutAPIView,
                    PollAPIView, ChoiceAPIView, TagAPIView, CategoryAPIView,
                    ProfileAPIView, GroupAPIView, VoteAPIView, PollResultsAPIView,
                    ChangePasswordAPIView, UserSelfUpdateAPIView, PasswordResetRequestAPIView,
                    PasswordResetAPIView, LandingPageAPIView)
from .views import vote_view, poll_results_view

app_name = "polls"

urlpatterns = [
    # schemas
    path(
        "openapi/",
        get_schema_view(
            title="Polls App", description="API for all schemas", version="1.0.0"
        ),
        name="openapi-schema",
    ),

    # Landing Page
    path('', LandingPageAPIView.as_view(), name='landing_page'),

    # Authentication
    path('accounts/login/', UserLoginAPIView.as_view(), name='user-login'),
    path('accounts/signup/', UserRegisterAPIView.as_view(), name='user-register'),
    path('accounts/logout/', UserLogoutAPIView.as_view(), name='user-logout'),
    path('accounts/refresh/', TokenRefreshView.as_view(), name='user-refresh-access'),
    # Change password
    path('accounts/password/change/', ChangePasswordAPIView.as_view(), name='user-change-password'),
    # Password reset request
    path('accounts/password/reset/', PasswordResetRequestAPIView.as_view(), name='password_reset_request'),
    # Password reset confirmation
    path('accounts/password/reset/confirm/<str:uidb64>/<str:token>/', PasswordResetAPIView.as_view(),
         name='password_reset_confirm'),

    # Polls
    path('polls/', PollAPIView.as_view(), name='poll-list-create'),
    path('polls/<int:pk>/', PollAPIView.as_view(), name='poll-detail'),

    # Vote
    path('vote/<int:poll_id>/', vote_view, name='vote-poll'),
    path('api/vote/<int:poll_id>/', VoteAPIView.as_view(), name='vote-poll-api'),

    # Polls Results
    path('poll_results/', poll_results_view, name='poll-results'),
    path('api/poll_results/', PollResultsAPIView.as_view(), name='poll-results-api'),

    # Profile
    path('profile/', ProfileAPIView.as_view(), name='user-profile'),
    path('user_update/', UserSelfUpdateAPIView.as_view(), name='user-self-update'),

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
