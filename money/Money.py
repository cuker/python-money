# -*- coding: utf-8 -*-
import exceptions
from decimal import Decimal

_CURRENCY_PROVIDER = None

def currency_provider():
    return _CURRENCY_PROVIDER

def set_currency_provider(provider):
    global _CURRENCY_PROVIDER
    _CURRENCY_PROVIDER = provider

class Currency(object):
    def __init__(self, code="", numeric="999", name="", countries=[]):
        self.code = code
        self.numeric = numeric
        self.name = name
        self.countries = countries
        self.exchange_rate = None
    def __repr__(self):
        return self.code
    def __eq__(self, other):
        if isinstance(other, Currency) or hasattr(other, 'code'):
            return self.code == other.code
        if isinstance(other, basestring):
            return self.code == other
        return False #don't know how to compare otherwise

class IncorrectMoneyInputError(exceptions.Exception):
    def __init__(self):
        return
    def __str__(self):
        return "Incorrectly formatted monetary input!"

class Money(object):
    def __init__ (self, amount=Decimal("0.0"), currency=None, allow_conversion=False):
        if not isinstance(amount, Decimal):
            amount = Decimal(amount)
        self.amount = amount
        self.allow_conversion = allow_conversion
        if not currency:
            self.currency = currency_provider().get_default()
        else:
            if not isinstance(currency, Currency):
                currency =currency_provider()[str(currency).upper()] #consider, may result in lots of db queries...
            self.currency = currency
    def __repr__(self):
        return '%s %5.2f' % (self.currency, self.amount)
    def __abs__(self):
        return Money(amount=abs(self.amount), currency=self.currency)
    def __pos__(self):
        return Money(amount=self.amount, currency=self.currency)
    def __neg__(self):
        return Money(amount=-self.amount, currency=self.currency)
    def __add__(self, other):
        if isinstance(other, Money):
            if self.currency == other.currency:
                return Money(amount = self.amount + other.amount, currency = self.currency)
            else: 
                assert self.allow_conversion
                s = self.convert_to_default()
                other = other.convert_to_default()
                return Money(amount = s.amount + other.amount, currency = currency_provider().get_default())
        else:
            return Money(amount = self.amount + other, currency = self.currency)
    def __sub__(self, other):
        if isinstance(other, Money):
            if self.currency == other.currency:
                return Money(amount = self.amount - other.amount, currency = self.currency)
            else: 
                assert self.allow_conversion
                s = self.convert_to_default()
                other = other.convert_to_default()
                return Money(amount = s.amount - other.amount, currency = currency_provider().get_default())
        else:
            return Money(amount = self.amount - other, currency = self.currency)
    def __mul__(self, other):
        if isinstance(other, Money):
            raise TypeError, 'can not multiply monetary quantities'
        else:
            return Money(amount = self.amount*other, currency = self.currency)
    def __div__(self, other):
        if isinstance(other, Money):
            raise TypeError, 'can not divide monetary quantities'
        else:
            return Money(self.amount / other, currency = self.currency)
    def __rmod__(self, other):
        """
        Calculate percentage of an amount.  The left-hand side of the operator must be a numeric value.  E.g.:
        >>> money = Money.Money(200, "USD")
        >>> 5 % money
        USD 10.00
        """
        if isinstance(other, Money):
            raise TypeError, 'invalid monetary operation'
        else:
            return Money(amount = other * self.amount / 100, currency = self.currency)
    def convert_to_default(self):
        if self.currency == currency_provider().get_default():
            return self.copy()
        assert self.currency.exchange_rate, 'No exchange rate defined for: %s' % self.currency
        return Money(amount = self.amount / self.currency.exchange_rate, currency=currency_provider().get_default())
    def convert_to(self, currency):
        """
        Convert from one currency to another.
        """
        assert currency.exchange_rate, 'No exchange rate defined'
        if self.currency == currency_provider().get_default():
            ret = self.copy()
        else:
            ret = self.convert_to_default()
        ret.amount *= currency.exchange_rate
        ret.currency = currency
        return ret
    def quantize(self, *args, **kwargs):
        return Money(amount = self.amount.quantize(*args, **kwargs), currency=self.currency)
    def copy(self):
        return Money(amount=self.amount, currency=self.currency)
    def __format__(self, *args, **kwargs):
        return self.amount.__format__(*args, **kwargs)
    def __float__(self):
        return float(self.amount)
    def __int__(self):
        return int(self.amount)
    def __nonzero__(self):
        return self.amount.__nonzero__()
    __radd__ = __add__
    __rsub__ = __sub__
    __rmul__ = __mul__
    __rdiv__ = __div__

    #
    # Override comparison operators
    #
    def __eq__(self, other):
        if isinstance(other, Money):
            return (self.amount == other.amount) and (self.currency == other.currency)
        return self.amount == other
    def __ne__(self, other):
        result = self.__eq__(other)
        if result is NotImplemented:
            return result
        return not result
    def __lt__(self, other):
        if isinstance(other, Money):
            if (self.currency == other.currency):
                return (self.amount < other.amount)
            else:
                raise TypeError, 'can not compare different currencies'
        else:
            return self.amount < other
    def __gt__(self, other):
        if isinstance(other, Money):
            if (self.currency == other.currency):
                return (self.amount > other.amount)
            else:
                raise TypeError, 'can not compare different currencies'
        else:
            return self.amount > other
    def __le__(self, other):
        return self < other or self == other
    def __ge__(self, other):
        return self > other or self == other

    #
    # Miscellaneous helper methods
    #

    def allocate(self, ratios):
        """
        Allocates a sum of money to several accounts.
        """
        total = sum(ratios)
        remainder = self.amount
        results = []
        for i in range(0, len(ratios)):
            results.append(Money(amount = self.amount * ratios[i] / total, currency = self.currency))
            remainder -= results[i].amount
        i = 0
        while i < remainder:
            results[i].amount += Decimal("0.01")
            i += 1
        return results

    def spell_out(self):
        """
        Spells out a monetary amount.  E.g. "Two-hundred and twenty-six dollars and seventeen cents."
        """
        pass # TODO

    @classmethod
    def from_string(cls, s):
        """
        Parses a properly formatted string and extracts the monetary value and currency
        """
        s = str(s).strip()
        sign = 1
        if s.startswith('-'):
            sign = -1
            s = s[1:].strip()
        try:
            amount = Decimal(s)
            currency = currency_provider().get_default()
        except:
            try:
                currency, amount = s.split(' ',1)
                currency = currency_provider()[currency.strip().upper()]
                amount = Decimal(amount.strip())
            except:
                raise IncorrectMoneyInputError
        return cls(amount*sign, currency)

