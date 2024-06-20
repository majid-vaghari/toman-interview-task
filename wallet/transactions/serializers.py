from decimal import Decimal

from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from rest_framework import serializers

from .models import Transaction, Wallet
from .validators import validate_positive_amount, FutureDateValidator


class TransactionNestedSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Transaction
        fields = ['uuid', 'amount', 'scheduled_time',
                  'status', 'error_message', 'created', 'updated']


class WalletSerializer(serializers.HyperlinkedModelSerializer):
    outgoing_transactions = TransactionNestedSerializer(
        many=True, read_only=True)
    incoming_transactions = TransactionNestedSerializer(
        many=True, read_only=True)

    class Meta:
        model = Wallet
        fields = ['url', 'uuid', 'balance', 'created', 'updated',
                  'outgoing_transactions', 'incoming_transactions']
        read_only_fields = ['ur', 'uuid', 'balance', 'created', 'updated']


class DepositSerializer(serializers.Serializer):
    amount = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=Decimal('0.01'),
        write_only=True,
        label=_('Amount'),
        help_text=_('The amount of the deposit.'),
        validators=[
            validate_positive_amount,
        ],
    )


class WithdrawRequestSerializer(serializers.Serializer):
    amount = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=Decimal('0.01'),
        label=_('Amount'),
        help_text=_('The amount of the withdrawal.'),
        validators=[
            validate_positive_amount,
        ]
    )
    scheduled_time = serializers.DateTimeField(
        label=_('Scheduled Time'),
        help_text=_('The scheduled time of the withdrawal.'),
        validators=[
            FutureDateValidator(minutes=1),
        ]
    )
    target = serializers.UUIDField(
        label=_('Target'),
        help_text=_('The wallet to which the withdrawal is made.'),
    )

    def validate_target(self, value):
        if str(value) == self.context['view'].kwargs['pk']:
            raise serializers.ValidationError(
                _('You cannot craete a withdraw request to yourself.'))
        return value
