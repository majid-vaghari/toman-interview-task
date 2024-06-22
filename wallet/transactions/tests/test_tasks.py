from decimal import Decimal
from time import sleep

from django.test import TestCase
from django.utils import timezone

from transactions.models import Wallet, Transaction
from transactions.tasks import process_withdrawal, request_transactions


TRANSACTION_TESTS = [
    {
        'amount': Decimal('20.00'),
        'status': 'SUCCESS',
        'sender_balance': Decimal('80.00'),
        'receiver_balance': Decimal('120.00'),
    },
    {
        'amount': Decimal('120.00'),
        'status': 'FAILED',
        'sender_balance': Decimal('100.00'),
        'receiver_balance': Decimal('100.00'),
    },
]


class TasksTestCase(TestCase):
    def setUp(self):
        self.sender = Wallet.objects.create(balance=Decimal('100.00'))
        self.receiver = Wallet.objects.create(balance=Decimal('100.00'))

    def test_create_transaction_implemented(self):
        """
        Test the implementation of the `create_transaction` function.

        This test case verifies that the `create_transaction` function is correctly implemented.
        It calls the `create_transaction` function and does not perform any assertions.

        Parameters:
            self (TestCase): The test case instance.

        Returns:
            None
        """
        request_transactions()

    def test_process_withdrawal_task(self):
        for transaction_test in TRANSACTION_TESTS:
            with self.subTest(name=transaction_test['status']):
                self.setUp()
                transaction = Transaction.objects.create(
                    sender=self.sender,
                    receiver=self.receiver,
                    amount=transaction_test['amount'],
                    scheduled_time=timezone.now() + timezone.timedelta(seconds=1),
                )
                sleep(2)
                process_withdrawal(str(transaction.uuid))
                transaction.refresh_from_db()
                self.assertEqual(transaction.status,
                                 transaction_test['status'])
                self.sender.refresh_from_db()
                self.receiver.refresh_from_db()
                self.assertEqual(self.sender.balance,
                                 transaction_test['sender_balance'])
                self.assertEqual(self.receiver.balance,
                                 transaction_test['receiver_balance'])
