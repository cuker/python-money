from django.db import models
from django.utils.encoding import smart_unicode
from django.db.models import signals
from django.conf import settings
from django import forms

from money import Money, CURRENCY

__all__ = ('MoneyField', 'CurrencyField')

def strcurrency(val):
    if hasattr(val, 'code'):
        return val.code
    return str(val)

class MoneyProxy(Money):
    def __init__(self, field, instance, amount, currency):
        self.field = field
        self.instance = instance
        super(MoneyProxy, self).__init__(amount, currency)
    
    def _set_amount(self, amount):
        self._amount = amount
        setattr(self.instance, self.field.value_field, amount)
        
    def _get_amount(self):
        return self._amount
    
    def _set_currency(self, currency):
        self._currency = currency
        setattr(self.instance, self.field.currency_field, strcurrency(currency))
        
    def _get_currency(self):
        return self._currency
        
    amount = property(_get_amount, _set_amount)
    currency = property(_get_currency, _set_currency)

class MoneyField(object):
    """
    Provides a currency instance to any object through value/currency fields.
    """

    def __init__(self, value_field, currency_field):
        self.value_field = value_field
        self.currency_field = currency_field

    def contribute_to_class(self, cls, name):
        self.name = name
        cls._meta.add_virtual_field(self)

        # For some reason I don't totally understand, using weakrefs here doesn't work.
        signals.pre_init.connect(self.instance_pre_init, sender=cls, weak=False)

        # Connect myself as the descriptor for this field
        setattr(cls, name, self)
        
    def _money_from_instance(self, instance):
        return MoneyProxy(self, instance, getattr(instance, self.value_field) or 0, getattr(instance, self.currency_field))

    def instance_pre_init(self, signal, sender, args, kwargs, **_kwargs):
        if self.name in kwargs:
            value = kwargs.pop(self.name)
            if isinstance(value, Money):
                kwargs[self.value_field] = value.amount
                kwargs[self.currency_field] = value.currency.code
            else:
                kwargs[self.value_field] = value

    def __get__(self, instance, instance_type=None):
        if instance is None:
            return self

        return self._money_from_instance(instance)

    def __set__(self, instance, value):
        if instance is None:
            raise AttributeError, u"%s must be accessed via instance" % self.name

        amount = None
        currency = None
        if value is not None:
            amount = value.amount
            currency = value.currency.code
        
        setattr(instance, self.value_field, amount)
        setattr(instance, self.currency_field, currency)
    
    def get_db_prep_lookup(self, *args, **kwargs):
        raise NotImplemented
        
class CurrencyField(models.CharField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('max_length', 3)
        super(CurrencyField, self).__init__(*args, **kwargs)

    def south_field_triple(self):
        """
        Return a suitable description of this field for South.
        """
        # We'll just introspect ourselves, since we inherit.
        from south.modelsinspector import introspector
        field_class = "django.db.models.fields.CharField"
        args, kwargs = introspector(self)
        # That's our definition!
        return (field_class, args, kwargs)
    
    def formfield(self, **kwargs):
        defaults = dict(kwargs)
        if 'money.contrib.django.currencies' in settings.INSTALLED_APPS:
            from money.contrib.django.currencies.models import Currency
            def choices():
                for item in Currency.objects.active().iterator():
                    yield item.code, item.code
        else:
            def choices():
                for key in CURRENCY.iterkeys():
                    yield key, key
        defaults['widget'] = forms.Select(choices=choices())
        return super(CurrencyField, self).formfield(**defaults)
    
