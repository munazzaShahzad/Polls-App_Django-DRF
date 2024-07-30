from django.contrib import admin

from .models import Poll, Choice, User, Category, Tag, UserTagHistory, UserPollHistory

admin.site.register(Poll)
admin.site.register(Choice)
admin.site.register(User)
admin.site.register(Category)
admin.site.register(Tag)
admin.site.register(UserTagHistory)
admin.site.register(UserPollHistory)
