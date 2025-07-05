from django.contrib import admin
from .models import (
    User,
    Vendor,
    Content,
    EventPackage,
    Inquiry,
    Booking,
    Mood,
    HealingIntent,
    HealingActivity,
    Guide,
)


admin.site.register(User)
admin.site.register(Vendor)
admin.site.register(Content)
admin.site.register(EventPackage)
admin.site.register(Inquiry)
admin.site.register(Booking)
admin.site.register(Mood)
@admin.register(Guide)
class GuideAdmin(admin.ModelAdmin):
    list_display    = ("name", "expertise")
    search_fields   = ("name", "expertise", "bio")
    filter_horizontal = ("packages",)
@admin.register(HealingIntent)
class HealingIntentAdmin(admin.ModelAdmin):
    list_display = ("name", "recommended_duration", "emoji")
    search_fields = ("name", "description")


@admin.register(HealingActivity)
class HealingActivityAdmin(admin.ModelAdmin):
    list_display = ("title", "activity_type", "intent")
    search_fields = ("title", "description", "activity_type")
    list_filter = ("activity_type", "intent")
