from decimal import Decimal

from django.test import TestCase
from django.db.utils import IntegrityError
from django.core.exceptions import ValidationError
from django.utils import timezone

from transactions.models import Wallet, Transaction


class WalletModelTest(TestCase):
    def test_wallet_creation(self):
        wallet = Wallet.objects.create()
        self.assertEqual(wallet.balance, Decimal('0.00'))

    def test_wallet_creation_with_balance(self):
        wallet = Wallet.objects.create(balance=Decimal('100.00'))
        self.assertEqual(wallet.balance, Decimal('100.00'))

    def test_wallet_creation_with_negative_balance(self):
        with self.assertRaises(IntegrityError):
            Wallet.objects.create(balance=Decimal('-100.00'))

    def test_wallet_deposit(self):
        wallet = Wallet.objects.create(balance=Decimal('100.00'))
        wallet.deposit(Decimal('50.00'))
        wallet.refresh_from_db()
        self.assertEqual(wallet.balance, Decimal('150.00'))

    def test_negative_deposit(self):
        wallet = Wallet.objects.create(balance=Decimal('100.00'))
        with self.assertRaises(ValidationError):
            wallet.deposit(Decimal('-50.00'))

    def test_zero_deposit(self):
        wallet = Wallet.objects.create(balance=Decimal('100.00'))
        with self.assertRaises(ValidationError):
            wallet.deposit(Decimal('0.00'))


class TransactionModelTest(TestCase):
    def setUp(self):
        self.sender = Wallet.objects.create(balance=Decimal('100.00'))
        self.receiver = Wallet.objects.create(balance=Decimal('50.00'))

    def test_transaction_creation(self):
        transaction = Transaction.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            amount=Decimal('20.00'),
            scheduled_time=timezone.now() + timezone.timedelta(days=1),
        )
        self.assertEqual(transaction.sender, self.sender)
        self.assertEqual(transaction.receiver, self.receiver)
        self.assertEqual(transaction.amount, Decimal('20.00'))
        self.assertEqual(transaction.status, 'PENDING')
    
    def test_transaction_creation_with_invalid_scheduled_time(self):
        with self.assertRaises(ValidationError):
            Transaction(
                sender=self.sender,
                receiver=self.receiver,
                amount=Decimal('20.00'),
                scheduled_time=timezone.now() - timezone.timedelta(days=1),
            ).full_clean()
    def test_transaction_creation_with_invalid_amount(self):
        with self.assertRaises(IntegrityError):
            Transaction.objects.create(
                sender=self.sender,
                receiver=self.receiver,
                amount=Decimal('-20.00'),
                scheduled_time=timezone.now() + timezone.timedelta(days=1),
            )
