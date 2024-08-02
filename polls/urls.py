from django.urls import path, include

from .views import ProfileView, PollListView, PollDetailView

app_name = "polls"

urlpatterns = [
    path('', ProfileView.as_view(), name='profile'),
    path('polls_list/', PollListView.as_view(), name='poll_list'),
    path('<int:pk>/', PollDetailView.as_view(), name='poll_detail'),
]
