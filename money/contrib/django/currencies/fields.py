from django.db import models
from django.db.models import signals

from money import Money
from models import Currency

__all__ = ('MoneyField', 'CurrencyField')

def lookup_currency(currency):
    if not isinstance(currency, Currency):
        if hasattr(currency, 'code'):
            code = currency.code
        else:
            code = str(currency)
        return Currency.objects.get(code=code)
    return currency

class CurrencyField(models.ForeignKey):
    def __init__(self, *args, **kwargs):
        kwargs['limit_choices_to'] = {'enabled':True}
        super(CurrencyField, self).__init__(Currency, *args, **kwargs)
    
    def south_field_triple(self):
        """
        Return a suitable description of this field for South.
        """
        # We'll just introspect ourselves, since we inherit.
        from south.modelsinspector import introspector
        field_class = "django.db.models.ForeignKey"
        args, kwargs = introspector(self)
        # That's our definition!
        return (field_class, args, kwargs)

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
        currency = lookup_currency(currency)
        setattr(self.instance, self.field.currency_field, currency)
        
    def _get_currency(self):
        return getattr(self.instance, self.field.currency_field)
        
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
                kwargs[self.currency_field] = lookup_currency(value.currency)
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
            currency = lookup_currency(value.currency)
        
        setattr(instance, self.value_field, amount)
        setattr(instance, self.currency_field, currency)
    
    def get_db_prep_lookup(self, *args, **kwargs):
        raise NotImplemented
