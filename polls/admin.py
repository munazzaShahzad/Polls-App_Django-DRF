from django.contrib import admin

from .models import Poll, Choice, User, Category, Tag, UserTagHistory, UserPollHistory

admin.register(Poll)

