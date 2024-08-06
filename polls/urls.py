from django.urls import path, include
from rest_framework import routers

from .views import (ProfileView, PollListView, PollDetailView,  # tag_list, tag_detail,
                    TagViewSet, PollViewSet, ChoiceViewSet, GroupViewSet)

router = routers.DefaultRouter()
router.register(r'tags', TagViewSet)
router.register(r'polls', PollViewSet)
router.register(r'choices', ChoiceViewSet)
# router.register(r'groups', GroupViewSet)

app_name = "polls"

urlpatterns = [
    path('', ProfileView.as_view(), name='profile'),
    # path('tags/', tag_list),
    # path('tags/<int:pk>', tag_detail),
    path('test/', include(router.urls)),
    path('polls_list/', PollListView.as_view(), name='poll_list'),
    path('<int:pk>/', PollDetailView.as_view(), name='poll_detail'),
]
