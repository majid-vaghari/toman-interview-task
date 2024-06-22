from time import sleep

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from transactions.models import Transaction, Wallet
from transactions.tasks import process_withdrawal


class WalletApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.wallet_uuid = str(Wallet.objects.create().uuid)

    def test_wallet_creation(self):
        response = self.client.post(reverse('wallet-list'))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Wallet.objects.count(), 2)

    def test_retrieve_wallet(self):
        response = self.client.get(
            reverse('wallet-detail', kwargs={'pk': self.wallet_uuid}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['uuid'], self.wallet_uuid)

    def test_deposit(self):
        response = self.client.patch(reverse(
            'wallet-deposit', kwargs={'pk': self.wallet_uuid}), data={'amount': 100})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Wallet.objects.get(
            uuid=self.wallet_uuid).balance, 100)

class TransactionApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.sender_uuid = str(Wallet.objects.create(balance='100').uuid)
        self.receiver_uuid = str(Wallet.objects.create().uuid)
    
    def test_create_transaction(self):
        response = self.client.post(reverse('wallet-withdraw', kwargs={'pk': self.sender_uuid}), data={
            'target': self.receiver_uuid,
            'amount': 100,
            'scheduled_time': timezone.now() + timezone.timedelta(seconds=61),
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Transaction.objects.count(), 1)
        transaction = Transaction.objects.first()
        assert transaction
        self.assertEqual(str(transaction.sender.uuid), self.sender_uuid)
        self.assertEqual(str(transaction.receiver.uuid), self.receiver_uuid)
        self.assertEqual(transaction.amount, 100)

        transaction.scheduled_time -= timezone.timedelta(minutes=2)
        transaction.save()

        process_withdrawal(str(transaction.uuid))

        transaction.refresh_from_db()

        self.assertEqual(transaction.status, 'SUCCESS')
        self.assertEqual(Wallet.objects.get(uuid=self.sender_uuid).balance, 0)
        self.assertEqual(Wallet.objects.get(uuid=self.receiver_uuid).balance, 100)