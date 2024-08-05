import datetime

from django.contrib import admin

from .models import Poll, Choice, User, Category, Tag, UserTagHistory, UserPollHistory, UserProfile


class ExpiredPollsFilter(admin.SimpleListFilter):
    title = "Poll Status"
    parameter_name = "poll_status"

    def lookups(self, request, model_admin):
        return [
            ("Closed", "Closed Polls"),
            ("Open", "Open Polls"),
        ]

    def queryset(self, request, queryset):
        if self.value() == "Closed":
            return queryset.filter(
                expiry_date__lte=datetime.datetime.now(),
            )
        elif self.value() == "Open":
            return queryset.filter(
                expiry_date__gt=datetime.datetime.now(),
            )


class UserAdmin(admin.ModelAdmin):
    list_display = ["id", "username"]
    list_filter = ["is_staff"]


class PollAdmin(admin.ModelAdmin):
    list_display = ["id", "title"]
    ordering = ["-expiry_date"]
    list_filter = [ExpiredPollsFilter]


admin.site.register(Poll, PollAdmin)
admin.site.register(Choice)
admin.site.register(User, UserAdmin)
admin.site.register(UserProfile)
admin.site.register(Category)
admin.site.register(Tag)
admin.site.register(UserTagHistory)
admin.site.register(UserPollHistory)
