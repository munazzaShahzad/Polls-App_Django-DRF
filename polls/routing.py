from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/vote/(?P<poll_id>\d+)/$', consumers.VoteConsumer.as_asgi()),
    re_path(r'ws/poll_results/(?P<poll_id>\d+)/$', consumers.PollResultsConsumer.as_asgi()),
    re_path(r'ws/poll_results/$', consumers.NewPollConsumer.as_asgi()),
]
