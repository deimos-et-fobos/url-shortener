from django.contrib import admin
from .models import ShortURL

class ShortURLAdmin(admin.ModelAdmin):
    readonly_fields = ['last_access']
    list_filter = ['last_access']

admin.site.register(ShortURL, ShortURLAdmin)
