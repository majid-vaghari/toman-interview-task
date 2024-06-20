"""
This module contains Celery tasks for processing transactions.

The :func:`process_withdrawal` function is used to process withdrawal transactions.
"""
import logging
import os
import requests

from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db import transaction as db_transaction
from celery import shared_task

from .models import Wallet, Transaction

TRANSACTION_API_URL = os.environ.get('TRANSACTION_API_URL')

logger = logging.getLogger(__name__)


@shared_task
@db_transaction.atomic
def process_withdrawal(transaction_uuid: str) -> None:
    """
    Process the withdrawal task.

    Args:
        transaction_uuid (str): The UUID of the transaction.

    Returns:
        None

    This function is a shared task that is executed asynchronously. It
    retrieves the transaction with the given UUID, validates the
    transaction's scheduled time and amount, requests transactions,
    updates the balances of the sender and receiver wallets, and sets
    the status of the transaction to success. If any exception occurs
    during the processing, it is handled by the
    `handle_transaction_failure` function. Finally, the sender,
    receiver, and transaction objects are saved.

    Note: - The function is decorated with `@shared_task` to make it a
    shared task. - The function is decorated with
    `@db_transaction.atomic` to ensure that all database operations
    within the
      function are executed in a single transaction.

    """

    try:
        transaction = Transaction \
            .objects \
            .select_related('sender', 'receiver') \
            .select_for_update() \
            .get(uuid=transaction_uuid)
    except Transaction.DoesNotExist as e:
        logger.error(
            "Transaction with ID %s does not exist. Skipping withdrawal processing.",
            transaction_uuid,
        )
        raise e

    try:
        sender, receiver = transaction.sender, transaction.receiver

        validate_transaction_scheduled_time(transaction)
        validate_transaction_amount(sender, transaction)

        request_transactions(
            sender=sender.uuid,
            receiver=receiver.uuid,
            amount=transaction.amount,
            scheduled_time=transaction.scheduled_time
        )

        handle_transaction_success(sender, receiver, transaction)

    except Exception as e:
        handle_transaction_failure(transaction, e)
    finally:
        save_objects(sender, receiver, transaction)


def request_transactions(**kwargs) -> bool:
    """
    Sends a POST request to the TRANSACTION_API_URL with the given
    keyword arguments as data. If the TRANSACTION_API_URL is not set,
    raises a ValueError.

    :param kwargs: Keyword arguments to be sent as data in the POST
        request.
    :type kwargs: dict

    :return: True if the request was successful, False otherwise.
    :rtype: bool

    :raises ValueError: If the TRANSACTION_API_URL is not set.
    :raises requests.exceptions.RequestException: If an error occurs
        during the request.
    """
    if not TRANSACTION_API_URL:
        raise ValueError('Transaction API URL not set')

    try:
        response = requests.post(TRANSACTION_API_URL, data=kwargs, timeout=5)
        response.raise_for_status()
        return response.ok
    except requests.exceptions.RequestException as e:
        logger.error("An error occurred while requesting transactions: %s", e)
        raise e


def validate_transaction_scheduled_time(transaction: Transaction) -> None:
    if transaction.scheduled_time > timezone.now():
        time_remaining = (transaction.scheduled_time -
                          timezone.now()).total_seconds()
        raise ValidationError(
            _("Transaction cannot be processed before the scheduled time. Try after %(time_remaining)s seconds."),
            params={'time_remaining': time_remaining}
        )


def validate_transaction_amount(sender: Wallet, transaction: Transaction) -> None:
    if sender.balance < transaction.amount:
        raise ValidationError(
            _("Insufficient funds. Available balance: %(available_balance)s. "
              "Required amount: %(required_amount)s."),
            params={'available_balance': sender.balance,
                    'required_amount': transaction.amount},
        )


def handle_transaction_success(sender: Wallet, receiver: Wallet, transaction: Transaction) -> None:
    sender.balance -= transaction.amount
    receiver.balance += transaction.amount

    transaction.status = Transaction.Status.SUCCESS


def handle_transaction_failure(transaction: Transaction, e: Exception) -> None:
    logger.error(
        "Error occurred while processing withdrawal: %s. Transaction ID: %s",
        e,
        transaction.uuid,
    )
    transaction.status = Transaction.Status.FAILED
    transaction.error_message = str(e)


def save_objects(sender: Wallet, receiver: Wallet, transaction: Transaction) -> None:
    try:
        for obj in [sender, receiver, transaction]:
            obj.save()

    except Exception as e:
        logger.critical(
            "Unexpected error occurred while saving objects: %s. "
            "Transaction ID: %s. "
            "Can't recover. This will probably lead to data loss.",
            e,
            transaction.uuid,
        )
        raise e
