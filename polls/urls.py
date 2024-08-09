from django.urls import path, include
from rest_framework import routers

from .views import UserLoginAPIView
from .views import UserRegisterAPIView
from .views import UserLogoutAPIView
from .views import (ProfileView, PollListView, PollDetailView,  # tag_list, tag_detail,
                    TagViewSet, PollViewSet, ChoiceViewSet, GroupViewSet, UserViewSet)

router = routers.DefaultRouter()
router.register(r'tags', TagViewSet)
router.register(r'polls', PollViewSet)
router.register(r'choices', ChoiceViewSet)
router.register(r'users', UserViewSet)
# router.register(r'groups', GroupViewSet)

app_name = "polls"

urlpatterns = [
    path('', ProfileView.as_view(), name='profile'),
    path('users/', UserViewSet.as_view({'get': 'list'})),
    path('api/', include(router.urls)),
    path("login/", UserLoginAPIView.as_view(), name="user_login"),
    path("register/", UserRegisterAPIView().as_view(), name="user_register"),
    path("logout/", UserLogoutAPIView.as_view(), name="user_logout"),
    path('polls_list/', PollListView.as_view(), name='poll_list'),
    path('<int:pk>/', PollDetailView.as_view(), name='poll_detail'),
]
