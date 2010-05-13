from django.db import models
from django.conf import settings
import money

class CurrencyManager(models.Manager):
    def active(self):
        return self.all().filter(enabled=True)
    
    def default(self):
        return self.get(default=True)
    
    def __getitem__(self, code):
        try:
            return self.get(code=code)
        except self.model.DoesNotExist:
            return ORIGINAL_CURRENCIES[code]

class Currency(models.Model, money.Currency):
    name = models.CharField(max_length=60)
    code = models.CharField(max_length=5, unique=True)
    numeric = models.CharField(max_length=5, unique=True)
    enabled = models.BooleanField(default=True, db_index=True)
    exchange_rate = models.DecimalField(max_digits=10, decimal_places=5)
    
    default = models.BooleanField(default=False, db_index=True)
    
    if 'countries' in settings.INSTALLED_APPS:
        from countries.models import Country
        countries = models.ManyToManyField(Country)
    
    objects = CurrencyManager()
    
    def __unicode__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if self.default and self.pk:
            type(self).objects.exclude(pk=self.pk, default=False).update(default=False)
        return models.Model.save(self, *args, **kwargs)

ORIGINAL_CURRENCIES = money.CURRENCY
money.CURRENCY = Currency.objects
money.get_default_currency = lambda: Currency.objects.default

def _load_currencies():
    for key, value in ORIGINAL_CURRENCIES.iteritems():
        if key == 'XXX': continue
        Currency.objects.get_or_create(name=value.name,
                                       code=value.code,
                                       numeric=value.numeric)
    try:
        Currency.objects.default()
    except Currency.DoesNotExist:
        new_default = Currency.objects['USD']
        new_default.default = True
        new_default.save()
