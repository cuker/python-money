import datetime

from django.db import models
from django.utils.translation import ugettext as _

from money.contrib.django.currencies.fields import MoneyField, CurrencyField

class LedgerException(Exception):
    pass

TX_CHOICES = (
    ('A', _('add')),
    ('W', _('withdraw')),
    ('M', _('move')),
)

class Account(models.Model):
    currency = CurrencyField()
    _balance = models.DecimalField(max_digits=12, decimal_places=2, default=0, db_column='balance')
    balance = MoneyField('_balance', 'currency')

    modified = models.DateTimeField(auto_now=True, editable=False)
    created = models.DateTimeField(default=datetime.datetime.now, editable=False)
    
    def add(self, amount):
        self.balance += amount
        transaction = self._create_transaction('A', amount)
        self.save()
        transaction.save()
        return transaction

    def withdraw(self, amount):
        if self.balance < amount:
            raise LedgerException("Withdraw amount couldn't be more than account balance")
        self.balance -= amount
        transaction = self._create_transaction('W', amount)
        transaction.save()
        self.save()
        return transaction

    def move(self, amount, to_account):
        if self.balance < amount:
            raise LedgerException("Withdraw amount couldn't be more than account balance")
        if self.currency != to_account.currency:
            raise LedgerException("Different currencies")
        self.balance -= amount
        to_account.balance += amount
        transaction = self._create_transaction('M', amount, to_account)
        transaction.save()
        self.save()
        to_account.save()
        return transactions

    def _create_transaction(self, type, amount, recipient=None):
        if amount < 0:
            raise LedgerException("Invalid amount")
        recipient_balance = None
        if recipient:
            recipient_balance = recipient.balance
        ct = Transaction(account=self, type=type, 
                         recipient_account=recipient,
                         amount=amount,
                         balance=self.balance,
                         recipient_balance=recipient_balance,)
        return ct

class Transaction(models.Model):
    account = models.ForeignKey(Account, related_name='transactions')
    type = models.CharField(max_length=1, choices=TX_CHOICES)
    
    currency = CurrencyField()
    _amount = models.DecimalField(max_digits=11, decimal_places=2, default="0.00", db_column='amount')
    amount = MoneyField('_amount', 'currency')
    _balance = models.DecimalField(max_digits=11, decimal_places=2, default="0.00", db_column='balance')
    balance = MoneyField('_balance', 'currency')
    
    recipient_account = models.ForeignKey(Account, blank=True, null=True, related_name='move_transactions')
    _recipient_balance = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True, db_column='recipient_balance')
    recipient_balance = MoneyField('_recipient_balance', 'currency')

    created = models.DateTimeField(default=datetime.datetime.now, editable=False, db_index=True)
