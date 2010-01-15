from django.db import models
from money.contrib.django.models.fields import *

class Entity(models.Model):
    name = models.CharField(max_length=100)
    price_amount = models.DecimalField(max_digits=12, decimal_places=3)
    price_currency = models.CharField(max_length=3)
    price = MoneyField('price_amount', 'price_currency')
    
    def __unicode__(self):
        return self.name + " " + str(self.price)


class Entity_0_USD(models.Model):
    name = models.CharField(max_length=100)
    price_amount = models.DecimalField(max_digits=12, decimal_places=3, default=0)
    price_currency = models.CharField(max_length=3, default='USD')
    price = MoneyField('price_amount', 'price_currency')
    
    def __unicode__(self):
        return self.name + " " + str(self.price)


class Entity_USD(models.Model):
    name = models.CharField(max_length=100)
    price_amount = models.DecimalField(max_digits=12, decimal_places=3, default=0)
    price_currency = models.CharField(max_length=3, default='USD')
    price = MoneyField('price_amount', 'price_currency')
    
    def __unicode__(self):
        return self.name + " " + str(self.price)
