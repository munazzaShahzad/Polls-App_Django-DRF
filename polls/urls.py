from django.urls import path

from .views import PollListView, PollDetailView

app_name = "polls"

urlpatterns = [
    path('', PollListView.as_view(), name='poll_list'),
    path('new/', PollDetailView.as_view(), name='poll_create'),
    path('<int:pk>/', PollDetailView.as_view(), name='poll_detail'),
    path('<int:pk>/edit/', PollDetailView.as_view(), name='poll_edit'),
    path('<int:pk>/delete/', PollDetailView.as_view(), name='poll_delete'),
]
