from django.contrib import admin
from models import Currency

class CurrencyAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'enabled', 'exchange_rate']
    list_filter = ['enabled', 'default']
    list_editable = ['enabled', 'exchange_rate']
    search_fields = ['name', 'code']

admin.site.register(Currency, CurrencyAdmin)
