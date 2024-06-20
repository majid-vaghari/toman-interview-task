import uuid

from django.utils.translation import gettext_lazy as _
from django.db import models, transaction
from django.db.models import Q, F

from .validators import (
    validate_positive_amount,
    validate_non_negative_amount,
    FutureDateValidator,
)


class TimeStampedModel(models.Model):
    created = models.DateTimeField(
        auto_now_add=True,
        editable=False,
        verbose_name=_("Created"),
        help_text=_("The date and time when this object was created."),
    )
    updated = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Updated"),
        help_text=_("The date and time when this object was last updated."),
    )

    class Meta:
        abstract = True


class UUIDModel(models.Model):
    uuid = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name=_("UUID"),
        help_text=_("A unique identifier for this object."),
    )

    class Meta:
        abstract = True


class Wallet(UUIDModel, TimeStampedModel):
    balance = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.0,
        verbose_name=_("Balance"),
        help_text=_("The current balance of the wallet."),
        validators=[
            validate_non_negative_amount,
        ],
    )

    @transaction.atomic
    def deposit(self, amount):
        """
        Deposit the given amount to the wallet.

        Args:
            amount (Decimal): The amount to deposit.

        Raises:
            Wallet.DoesNotExist: If no wallet with the given UUID exists.
            ValidationError: If the amount is not positive.

        Returns:
            None

        This method is decorated with `@transaction.atomic`, which ensures that the entire
        operation is treated as a single transaction. It first validates that the amount
        is positive using `validate_positive_amount`. Then, it retrieves the wallet with
        the given UUID using `Wallet.objects.select_for_update().get(uuid=self.uuid)`.
        Next, it updates the balance of the wallet by adding the given amount to it. After
        that, it calls `full_clean()` to validate the updated balance. Finally, it saves
        the updated wallet object.

        Note: The `select_for_update()` method is used to lock the wallet row in the database
        until the transaction is committed or rolled back, preventing any concurrent
        modifications to the wallet balance.
        """
        validate_positive_amount(amount)
        wallet = Wallet.objects.select_for_update().get(uuid=self.uuid)
        wallet.balance += amount
        wallet.full_clean()
        wallet.save()

    def __str__(self):
        return str(self.uuid)

    def __repr__(self):
        return f'Wallet<uuid={self.uuid}, balance={self.balance}>'

    class Meta:
        verbose_name = _("Wallet")
        verbose_name_plural = _("Wallets")

        constraints = [
            models.CheckConstraint(
                check=Q(balance__gte=0),
                name="positive_balance",
                violation_error_message=_(
                    "The balance must always be positive. Got %(show_value)s."
                ),
            ),
        ]


class Transaction(UUIDModel, TimeStampedModel):
    class Status(models.TextChoices):
        PENDING = 'PENDING', _('Pending')
        SUCCESS = 'SUCCESS', _('Success')
        FAILED = 'FAILED', _('Failed')

    sender = models.ForeignKey(
        Wallet,
        on_delete=models.CASCADE,
        related_name='outgoing_transactions',
        verbose_name=_("Sender Wallet"),
        help_text=_("The wallet from which the transaction is made."),
    )
    receiver = models.ForeignKey(
        Wallet,
        on_delete=models.CASCADE,
        related_name='incoming_transactions',
        verbose_name=_("Receiver Wallet"),
        help_text=_("The wallet to which the transaction is made."),
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_("Amount"),
        help_text=_("The amount of the transaction."),
        validators=[
            validate_positive_amount,
        ],
    )
    scheduled_time = models.DateTimeField(
        verbose_name=_("Scheduled Time"),
        help_text=_("The scheduled time of the transaction."),
        validators=[
            FutureDateValidator(),
        ],
    )
    status = models.CharField(
        max_length=10,
        choices=Status,
        default=Status.PENDING,
        editable=False,
        verbose_name=_("Status"),
        help_text=_("The status of the transaction."),
    )
    error_message = models.TextField(
        blank=True,
        max_length=1023,
        editable=False,
        verbose_name=_("Error Message"),
        help_text=_("The error message if the transaction failed."),
    )

    def __str__(self):
        return str(self.uuid)

    def __repr__(self):
        return f'Transaction<uuid={self.uuid}, from={self.sender}, to={self.receiver}, amount={self.amount}, scheduled_time={self.scheduled_time}, status={self.status}>'

    class Meta:
        verbose_name = _("Transaction")
        verbose_name_plural = _("Transactions")

        constraints = [
            models.CheckConstraint(
                check=Q(amount__gte=0),
                name="positive_amount",
                violation_error_message=_(
                    "The amount must be positive. Got %(show_value)s."
                ),
            ),
            models.CheckConstraint(
                check=~Q(sender=F('receiver')),
                name="sender_and_receiver_are_different",
                violation_error_message=_(
                    "Sender and receiver cannot be the same."
                ),
            ),
        ]
