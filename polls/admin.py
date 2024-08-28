import datetime

from django.contrib import admin
from django.utils import timezone
from django.contrib.auth.admin import UserAdmin

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


class CustomUserAdmin(UserAdmin):
    list_display = ["id", "username"]
    list_filter = ["is_staff"]

    # fieldsets for updating a user
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
        ('Additional info', {'fields': ('user_type',)}),  # Add user_type here
    )


class PollAdmin(admin.ModelAdmin):
    list_display = ["id", "title"]
    ordering = ["-expiry_date"]
    list_filter = [ExpiredPollsFilter]
    actions = ["close_polls"]

    @admin.action(description="Close selected polls")
    def close_polls(self, request, queryset):
        for poll in queryset:
            if poll.expiry_date > timezone.now():
                poll.expiry_date = timezone.now()
                poll.save()


admin.site.register(Poll, PollAdmin)
admin.site.register(Choice)
admin.site.register(User, CustomUserAdmin)
admin.site.register(UserProfile)
admin.site.register(Category)
admin.site.register(Tag)
admin.site.register(UserTagHistory)
admin.site.register(UserPollHistory)
