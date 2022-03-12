from django.contrib import admin

from .models import (Conference, ConferenceName, ReferencePaper, UserPaper)


class ConferenceAdmin(admin.ModelAdmin):
    list_display = ["conference", "year"]


class ReferencePaperAdmin(admin.ModelAdmin):
    list_display = ["title", "published_at"]


class UserPaperAdmin(admin.ModelAdmin):
    list_display = ["title", "owner"]


admin.site.register(Conference, ConferenceAdmin)
admin.site.register(ConferenceName)
admin.site.register(ReferencePaper, ReferencePaperAdmin)
admin.site.register(UserPaper, UserPaperAdmin)
